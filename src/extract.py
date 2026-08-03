"""
Module: extract.py
Description: Ingests raw transactional data from heterogeneous formats (CSV, JSON, XML) 
             and reference CSV files without applying cleaning or business calculations.
             Converts all transaction sources to a common technical schema.
"""

import pandas as pd
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict

# Esquema común estandarizado para todas las transacciones según la guía del laboratorio
COMMON_TRANSACTION_COLUMNS = [
    'sale_line_id',
    'sale_date',
    'store_id',
    'product_id',
    'quantity',
    'unit_price',
    'promotion_code',
    'payment_method'
]


def extract_sales_cali(file_path: Path) -> pd.DataFrame:
    """
    Extrae transacciones de la sede de Cali desde un archivo CSV.
    
    Args:
        file_path (Path): Ruta al archivo sales_cali.csv.
        
    Returns:
        pd.DataFrame: DataFrame con las transacciones estandarizadas al esquema común.
    """
    try:
        df = pd.read_csv(file_path)
        # Reordenar y asegurar que estén las columnas del esquema común
        df = df.reindex(columns=COMMON_TRANSACTION_COLUMNS)
        return df
    except Exception as e:
        print(f"[ERROR] Fallo al extraer sales_cali.csv: {e}")
        raise


def extract_sales_bogota(file_path: Path) -> pd.DataFrame:
    """
    Extrae transacciones de la sede de Bogotá desde un archivo JSON.
    
    Args:
        file_path (Path): Ruta al archivo sales_bogota.json.
        
    Returns:
        pd.DataFrame: DataFrame con las transacciones estandarizadas al esquema común.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        df = pd.DataFrame(data)
        # Mapear columnas al esquema estándar
        df = df.reindex(columns=COMMON_TRANSACTION_COLUMNS)
        return df
    except Exception as e:
        print(f"[ERROR] Fallo al extraer sales_bogota.json: {e}")
        raise


def extract_sales_medellin(file_path: Path) -> pd.DataFrame:
    """
    Extrae transacciones de la sede de Medellín desde un archivo XML.
    
    Args:
        file_path (Path): Ruta al archivo sales_medellin.xml.
        
    Returns:
        pd.DataFrame: DataFrame con las transacciones estandarizadas al esquema común.
    """
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        records = []
        # Recorrer todos los elementos hijos (nodos de transacción o venta)
        for elem in root:
            record = {}
            for child in elem:
                record[child.tag] = child.text
            if record:
                records.append(record)
                
        df = pd.DataFrame(records)
        
        # Asegurar presencia de todas las columnas del esquema común
        for col in COMMON_TRANSACTION_COLUMNS:
            if col not in df.columns:
                df[col] = None
                
        df = df[COMMON_TRANSACTION_COLUMNS]
        return df
    except Exception as e:
        print(f"[ERROR] Fallo al extraer sales_medellin.xml: {e}")
        raise


def extract_reference_data(raw_dir: Path) -> Dict[str, pd.DataFrame]:
    """
    Extrae las tablas maestras de referencia en formato CSV.
    
    Args:
        raw_dir (Path): Carpeta donde residen los archivos raw.
        
    Returns:
        Dict[str, pd.DataFrame]: Diccionario con DataFrames de productos, tiendas, promociones y metas.
    """
    try:
        return {
            'products': pd.read_csv(raw_dir / 'products.csv'),
            'stores': pd.read_csv(raw_dir / 'stores.csv'),
            'promotions': pd.read_csv(raw_dir / 'promotions.csv'),
            'monthly_targets': pd.read_csv(raw_dir / 'monthly_targets.csv')
        }
    except Exception as e:
        print(f"[ERROR] Fallo al extraer tablas de referencia: {e}")
        raise


def extract_all_transactions(raw_dir: Path) -> pd.DataFrame:
    """
    Lee las 3 fuentes heterogéneas y las consolida en un único DataFrame en crudo.
    
    Args:
        raw_dir (Path): Carpeta que contiene los archivos raw.
        
    Returns:
        pd.DataFrame: DataFrame consolidado sin transformaciones aplicadas.
    """
    df_cali = extract_sales_cali(raw_dir / 'sales_cali.csv')
    df_bogota = extract_sales_bogota(raw_dir / 'sales_bogota.json')
    df_medellin = extract_sales_medellin(raw_dir / 'sales_medellin.xml')
    
    # Concatenar en crudo manteniendo el esquema común
    raw_transactions = pd.concat([df_cali, df_bogota, df_medellin], ignore_index=True)
    return raw_transactions