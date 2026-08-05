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
        df = pd.read_csv(file_path)
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
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

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
        tree = ET.parse(file_path)
        root = tree.getroot()

        records = []
        for elem in root:
            record = {}
            for child in elem:
                record[child.tag] = child.text
            if record:
                records.append(record)

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
    df_cali     = extract_sales_cali(raw_dir / 'sales_cali.csv')
    df_bogota   = extract_sales_bogota(raw_dir / 'sales_bogota.json')
    df_medellin = extract_sales_medellin(raw_dir / 'sales_medellin.xml')

    raw_transactions = pd.concat([df_cali, df_bogota, df_medellin], ignore_index=True)
    return raw_transactions