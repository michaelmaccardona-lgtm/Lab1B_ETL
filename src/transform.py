"""
Module: transform.py
Description: Handles profiling, cleaning, harmonization, and integration
             of transaction records with reference master tables.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any

def profile_raw_data(df_raw: pd.DataFrame) -> Dict[str, Any]:
    """
    Inspecciona y audita el DataFrame transaccional combinado en crudo.
    Retorna un diccionario estructurado con los hallazgos de calidad de datos.
    
    Args:
        df_raw (pd.DataFrame): DataFrame consolidado de transacciones en crudo.
        
    Returns:
        Dict[str, Any]: Diccionario con métricas de calidad de datos y conteo de errores.
    """
    total_rows = len(df_raw)
    
    # 1. Conteo de nulos por columna
    null_counts = df_raw.isnull().sum().to_dict()
    
    # 2. Identificar duplicados en sale_line_id (descartando nulos)
    non_null_ids = df_raw['sale_line_id'].dropna()
    duplicate_ids_count = non_null_ids.duplicated().sum()
    
    # 3. Cantidades no válidas (<= 0 o no numéricas)
    qty_numeric = pd.to_numeric(df_raw['quantity'], errors='coerce')
    invalid_quantities_count = (qty_numeric <= 0).sum() + qty_numeric.isnull().sum()
    
    # 4. Precios no válidos (<= 0 o no numéricos)
    price_numeric = pd.to_numeric(df_raw['unit_price'], errors='coerce')
    invalid_prices_count = (price_numeric <= 0).sum() + price_numeric.isnull().sum()
    
    # 5. Fechas no válidas
    parsed_dates = pd.to_datetime(df_raw['sale_date'], errors='coerce')
    invalid_dates_count = parsed_dates.isnull().sum()
    
    # 6. Valores únicos en categóricos
    unique_stores = df_raw['store_id'].dropna().unique().tolist()
    unique_payments = df_raw['payment_method'].dropna().unique().tolist()
    
    summary = {
        'total_rows': total_rows,
        'null_counts': null_counts,
        'duplicate_sale_line_ids': int(duplicate_ids_count),
        'invalid_quantities': int(invalid_quantities_count),
        'invalid_prices': int(invalid_prices_count),
        'invalid_dates': int(invalid_dates_count),
        'unique_stores': unique_stores,
        'unique_payment_methods': unique_payments
    }
    
    return summary


def print_profiling_report(summary: Dict[str, Any]) -> None:
    """
    Imprime un reporte legible en consola con las métricas del profiling.
    
    Args:
        summary (Dict[str, Any]): Resumen generado por profile_raw_data.
    """
    print("\n" + "="*50)
    print("        PROFILING SUMMARY (RAW TRANSACTIONS)")
    print("="*50)
    print(f"Total Raw Rows Ingested: {summary['total_rows']}")
    print("\n--- Missing Values per Column ---")
    for col, count in summary['null_counts'].items():
        print(f"  - {col}: {count} nulls")
        
    print("\n--- Data Quality Issues Detected ---")
    print(f"  - Duplicate sale_line_ids : {summary['duplicate_sale_line_ids']}")
    print(f"  - Invalid/Null Quantities  : {summary['invalid_quantities']}")
    print(f"  - Invalid/Null Prices      : {summary['invalid_prices']}")
    print(f"  - Invalid/Null Dates       : {summary['invalid_dates']}")
    
    print("\n--- Categorical Field Values ---")
    print(f"  - Distinct Store IDs       : {summary['unique_stores']}")
    print(f"  - Payment Methods          : {summary['unique_payment_methods']}")
    print("="*50 + "\n")

def clean_and_harmonize_data(df_raw: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica reglas de limpieza y armonización a las transacciones en crudo
    basándose en los hallazgos del profiling.
    
    Args:
        df_raw (pd.DataFrame): Transacciones en crudo.
        
    Returns:
        pd.DataFrame: Dataset de transacciones limpio y armonizado.
    """
    df = df_raw.copy()
    
    # 1. Limpieza de texto y espacios en blanco
    for str_col in ['sale_line_id', 'store_id', 'product_id', 'promotion_code', 'payment_method']:
        if str_col in df.columns:
            df[str_col] = df[str_col].astype(str).str.strip()
            df[str_col] = df[str_col].replace({'nan': None, 'None': None, '': None})
            
    # Standardize casing for IDs and payment methods
    df['store_id'] = df['store_id'].str.upper()
    df['product_id'] = df['product_id'].str.upper()
    df['payment_method'] = df['payment_method'].str.title()
    
    # 2. Armonización de fechas (soporta múltiples formatos)
    df['sale_date'] = pd.to_datetime(df['sale_date'], errors='coerce', format='mixed')
    
    # 3. Conversión de tipos numéricos
    df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce')
    df['unit_price'] = pd.to_numeric(df['unit_price'], errors='coerce')
    
    # 4. Manejo consistente de códigos de promoción faltantes
    df['promotion_code'] = df['promotion_code'].fillna('NONE').str.upper()
    
    # 5. Eliminación de duplicados por sale_line_id (conservando la primera ocurrencia válida)
    df = df.dropna(subset=['sale_line_id'])
    df = df.drop_duplicates(subset=['sale_line_id'], keep='first')
    
    # 6. Rechazo de registros con valores inválidos
    valid_mask = (
        df['sale_date'].notnull() &
        df['quantity'].notnull() & (df['quantity'] > 0) &
        df['unit_price'].notnull() & (df['unit_price'] > 0)
    )
    
    clean_df = df[valid_mask].copy()
    
    # Formatear fecha a string YYYY-MM-DD estándar
    clean_df['sale_date'] = clean_df['sale_date'].dt.strftime('%Y-%m-%d')
    clean_df['quantity'] = clean_df['quantity'].astype(int)
    clean_df['unit_price'] = clean_df['unit_price'].astype(float)
    
    return clean_df

def transform_and_integrate_data(clean_df: pd.DataFrame, ref_data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Integra transacciones limpias con las tablas maestras (JOINs),
    calcula métricas financieras (gross_sales, discount, net_sales),
    extrae campos temporales y ejecuta validaciones de calidad (assertions).
    """
    df = clean_df.copy()
    
    # 1. Preparación de tablas maestras
    products = ref_data['products'].copy()
    stores = ref_data['stores'].copy()
    promotions = ref_data['promotions'].copy()
    
    # Estandarizar mayúsculas en llaves para asegurar JOIN correcto
    products['product_id'] = products['product_id'].astype(str).str.strip().str.upper()
    stores['store_id'] = stores['store_id'].astype(str).str.strip().str.upper()
    promotions['promotion_code'] = promotions['promotion_code'].astype(str).str.strip().str.upper()
    
    # 2. Relación de datos (JOINs)
    df = df.merge(products[['product_id', 'product_name', 'category']], on='product_id', how='left')
    df = df.merge(stores[['store_id', 'store_name', 'city', 'region']], on='store_id', how='left')
    df = df.merge(promotions[['promotion_code', 'discount_rate']], on='promotion_code', how='left')
    
    # Si no aplica promoción o no encuentra código, el descuento es 0%
    df['discount_rate'] = df['discount_rate'].fillna(0.0)
    
    # 3. Cálculos de Negocio
    df['gross_sales'] = df['quantity'] * df['unit_price']
    df['discount_amount'] = df['gross_sales'] * (df['discount_rate'] / 100.0)
    df['net_sales'] = df['gross_sales'] - df['discount_amount']
    
    # 4. Atributos Temporales
    dt_series = pd.to_datetime(df['sale_date'])
    df['year'] = dt_series.dt.year
    df['month'] = dt_series.dt.month
    df['week'] = dt_series.dt.isocalendar().week
    df['day_name'] = dt_series.dt.day_name()
    
    # 5. Validaciones de Calidad de Datos (Data Quality Assertions)
    assert df['sale_line_id'].is_unique, "[CRITICAL ERROR] sale_line_id contains non-unique values."
    assert df['net_sales'].isnull().sum() == 0, "[CRITICAL ERROR] net_sales contains null values."
    assert (df['net_sales'] >= 0).all(), "[CRITICAL ERROR] net_sales contains negative values."
    assert df['store_name'].isnull().sum() == 0, "[WARNING/ERROR] Unmapped store_id detected during JOIN."
    assert df['product_name'].isnull().sum() == 0, "[WARNING/ERROR] Unmapped product_id detected during JOIN."
    
    return df