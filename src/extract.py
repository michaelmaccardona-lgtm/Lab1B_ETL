"""
Extracción de datos

En este archivo nos conectamos a los datos originales que nos enviaron de cada ciudad. Cali nos envió un archivo CSV, Bogotá un JSON y Medellín un XML. Lo que hacemos aquí es leer esa información tal cual viene y unificar los nombres de las columnas para que queden iguales en todas partes. Al final, juntamos todo en una sola tabla para poder procesarla más adelante, pero aquí todavía no hacemos cálculos ni borramos información.
"""

import pandas as pd
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict

# Common schema for all transactions
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
    Extrae transacciones de Cali desde CSV.
    Columnas originales ya coinciden con el esquema común.
    """
    try:
        # Usa pandas para leer el archivo CSV directamente
        df = pd.read_csv(file_path)
        
        # reindex() asegura que las columnas del DataFrame queden exactamente en el orden 
        # del esquema común. Si falta una columna, la crea con valores NaN (nulos).
        df = df.reindex(columns=COMMON_TRANSACTION_COLUMNS)
        
        print(f"  [EXTRACT] Cali CSV: {len(df)} records loaded.")
        return df
    except Exception as e:
        print(f"[ERROR] Fallo al extraer sales_cali.csv: {e}")
        raise


def extract_sales_bogota(file_path: Path) -> pd.DataFrame:
    """
    Extrae transacciones de Bogotá desde JSON.
    Mapeo de columnas:
        id_linea        -> sale_line_id
        fecha           -> sale_date
        sucursal        -> store_id
        codigo_producto -> product_id
        unidades        -> quantity
        precio          -> unit_price
        promocion       -> promotion_code
        medio_pago      -> payment_method
    """
    try:
        # Abre el archivo JSON en modo lectura ('r')
        with open(file_path, 'r', encoding='utf-8') as f:
            # json.load() convierte el texto del archivo JSON en una lista de diccionarios en Python
            data = json.load(f)

        # Convierte esa lista de diccionarios en una tabla (DataFrame) de Pandas
        df = pd.DataFrame(data)

        # Renombrar columnas al esquema común
        df = df.rename(columns={
            'id_linea':        'sale_line_id',
            'fecha':           'sale_date',
            'sucursal':        'store_id',
            'codigo_producto': 'product_id',
            'unidades':        'quantity',
            'precio':          'unit_price',
            'promocion':       'promotion_code',
            'medio_pago':      'payment_method'
        })

        df = df.reindex(columns=COMMON_TRANSACTION_COLUMNS)
        print(f"  [EXTRACT] Bogotá JSON: {len(df)} records loaded.")
        return df
    except Exception as e:
        print(f"[ERROR] Fallo al extraer sales_bogota.json: {e}")
        raise


def extract_sales_medellin(file_path: Path) -> pd.DataFrame:
    """
    Extrae transacciones de Medellín desde XML.
    Mapeo de columnas:
        line_id     -> sale_line_id
        date        -> sale_date
        branch_code -> store_id
        sku         -> product_id
        units       -> quantity
        unit_value  -> unit_price
        promo_code  -> promotion_code
        payment     -> payment_method
    """
    try:
        # Parseamos el archivo XML para leer su estructura de árbol
        tree = ET.parse(file_path)
        root = tree.getroot() # Obtenemos el nodo principal (raíz)

        records = []
        # Iteramos por cada nodo hijo (cada transacción individual)
        for elem in root:
            record = {}
            # Iteramos por cada etiqueta dentro de la transacción (date, sku, etc.)
            for child in elem:
                record[child.tag] = child.text # Guardamos el valor de la etiqueta en el diccionario
            if record:
                records.append(record)

        # Convertimos la lista de diccionarios a un DataFrame
        df = pd.DataFrame(records)

        # Renombrar columnas al esquema común
        df = df.rename(columns={
            'line_id':     'sale_line_id',
            'date':        'sale_date',
            'branch_code': 'store_id',
            'sku':         'product_id',
            'units':       'quantity',
            'unit_value':  'unit_price',
            'promo_code':  'promotion_code',
            'payment':     'payment_method'
        })

        df = df.reindex(columns=COMMON_TRANSACTION_COLUMNS)
        print(f"  [EXTRACT] Medellín XML: {len(df)} records loaded.")
        return df
    except Exception as e:
        print(f"[ERROR] Fallo al extraer sales_medellin.xml: {e}")
        raise


def extract_reference_data(raw_dir: Path) -> Dict[str, pd.DataFrame]:
    """
    Extrae las tablas maestras de referencia en formato CSV.
    """
    try:
        return {
            'products':        pd.read_csv(raw_dir / 'products.csv'),
            'stores':          pd.read_csv(raw_dir / 'stores.csv'),
            'promotions':      pd.read_csv(raw_dir / 'promotions.csv'),
            'monthly_targets': pd.read_csv(raw_dir / 'monthly_targets.csv')
        }
    except Exception as e:
        print(f"[ERROR] Fallo al extraer tablas de referencia: {e}")
        raise


def extract_all_transactions(raw_dir: Path) -> pd.DataFrame:
    """
    Lee las 3 fuentes heterogéneas y las consolida en un único DataFrame en crudo.
    """
    # Extraemos independientemente cada archivo usando su función específica
    df_cali     = extract_sales_cali(raw_dir / 'sales_cali.csv')
    df_bogota   = extract_sales_bogota(raw_dir / 'sales_bogota.json')
    df_medellin = extract_sales_medellin(raw_dir / 'sales_medellin.xml')

    # pd.concat() une los tres DataFrames uno debajo del otro. 
    # ignore_index=True reinicia los índices para que vayan del 0 al total de filas.
    raw_transactions = pd.concat([df_cali, df_bogota, df_medellin], ignore_index=True)
    return raw_transactions