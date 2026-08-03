"""
Module: load.py
Description: Handles data persistence by exporting the integrated analytical DataFrame 
             to a CSV file in data/processed and writing it into a SQLite database.
"""

import sqlite3
import pandas as pd
from pathlib import Path

def save_to_csv(df: pd.DataFrame, output_path: Path) -> None:
    """
    Guarda el DataFrame integrado en formato CSV dentro de data/processed.
    
    Args:
        df (pd.DataFrame): DataFrame integrado y validado.
        output_path (Path): Ruta completa del archivo CSV de salida.
    """
    try:
        # Asegurar que el directorio exista
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False, encoding='utf-8')
        print(f"[LOAD] Archivo CSV procesado guardado con éxito en: {output_path}")
    except Exception as e:
        print(f"[ERROR] Fallo al guardar el archivo CSV: {e}")
        raise

def load_to_sqlite(df: pd.DataFrame, db_path: Path, table_name: str = 'sales_analytics') -> None:
    """
    Carga el DataFrame integrado en la base de datos SQLite.
    
    Args:
        df (pd.DataFrame): DataFrame integrado y validado.
        db_path (Path): Ruta a la base de datos SQLite.
        table_name (str): Nombre de la tabla destino en SQLite.
    """
    try:
        # Asegurar que la carpeta database/ exista
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(db_path)
        
        # Guardar en SQLite (if_exists='replace' para mantener idempotencia en re-ejecuciones)
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        
        # Verificar la cantidad de filas cargadas
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        row_count = cursor.fetchone()[0]
        conn.close()
        
        print(f"[LOAD] Carga a SQLite completada. Tabla '{table_name}' creada con {row_count} registros.")
    except Exception as e:
        print(f"[ERROR] Fallo al cargar los datos en SQLite: {e}")
        raise