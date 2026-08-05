"""
Module: load.py
Description: Handles data persistence by exporting the integrated analytical DataFrame 
             to a CSV file in data/processed and writing it into a SQLite database.
             Also loads reference tables (monthly_targets) needed for analytical queries.
"""

import sqlite3
import pandas as pd
from pathlib import Path
from typing import Dict

def save_to_csv(df: pd.DataFrame, output_path: Path) -> None:
    """
    Guarda el DataFrame integrado en formato CSV dentro de data/processed.
    """
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False, encoding='utf-8')
        print(f"[LOAD] Archivo CSV procesado guardado con éxito en: {output_path}")
    except Exception as e:
        print(f"[ERROR] Fallo al guardar el archivo CSV: {e}")
        raise


def load_to_sqlite(df: pd.DataFrame, db_path: Path, table_name: str = 'sales_analytics') -> None:
    """
    Carga el DataFrame integrado en la base de datos SQLite.
    """
    try:
        db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(db_path)

        df.to_sql(table_name, conn, if_exists='replace', index=False)

        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        row_count = cursor.fetchone()[0]
        conn.close()

        print(f"[LOAD] Carga a SQLite completada. Tabla '{table_name}' creada con {row_count} registros.")
    except Exception as e:
        print(f"[ERROR] Fallo al cargar los datos en SQLite: {e}")
        raise


def load_reference_tables(ref_data: Dict[str, pd.DataFrame], db_path: Path) -> None:
    """
    Carga las tablas de referencia en SQLite para poder usarlas en queries analíticas.
    En particular, 'monthly_targets' es requerida para el cálculo de cumplimiento de metas
    (Requerimiento 3 – Activity 11).

    Args:
        ref_data (Dict[str, pd.DataFrame]): Diccionario con DataFrames de referencia
                                            (products, stores, promotions, monthly_targets).
        db_path (Path): Ruta a la base de datos SQLite.
    """
    try:
        conn = sqlite3.connect(db_path)

        for table_name, df in ref_data.items():
            df.to_sql(table_name, conn, if_exists='replace', index=False)
            print(f"[LOAD] Tabla de referencia '{table_name}' cargada con {len(df)} registros.")

        conn.close()
    except Exception as e:
        print(f"[ERROR] Fallo al cargar las tablas de referencia en SQLite: {e}")
        raise