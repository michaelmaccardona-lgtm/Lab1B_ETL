"""
En esta parte guardamos todo el trabajo que ya hicimos. 
Tomamos la tabla final que salió de la transformación y la exportamos a un CSV nuevecito.
Pero lo más importante es que también guardamos los datos en una base de datos de SQLite (retail_analytics.db) para poder hacerle consultas SQL más adelante.
Usamos la opción de 'replace' para que si corremos el código varias veces, no se nos dupliquen los datos (a esto el profe le llama idempotencia).
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
        # Crea la carpeta si no existe (por ejemplo, data/processed)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Guarda el DataFrame de Pandas como un archivo CSV sin incluir la columna de índices
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
        # Asegura que la carpeta database exista
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Conecta a la base de datos SQLite (la crea si no existe)
        conn = sqlite3.connect(db_path)

        # Guarda los datos. if_exists='replace' asegura que si volvemos a correr el código, 
        # borre la tabla vieja y ponga la nueva (Idempotencia)
        df.to_sql(table_name, conn, if_exists='replace', index=False)

        # Verifica cuántas filas se cargaron realmente usando una consulta SQL
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
        # Abre la conexión a la base de datos SQLite
        conn = sqlite3.connect(db_path)

        # Recorre cada tabla maestra del diccionario (products, stores, etc.)
        for table_name, df in ref_data.items():
            # Guarda cada tabla maestra en la base de datos para poder unirlas (JOIN) en SQL después
            df.to_sql(table_name, conn, if_exists='replace', index=False)
            print(f"[LOAD] Tabla de referencia '{table_name}' cargada con {len(df)} registros.")

        conn.close() # Siempre es importante cerrar la conexión
    except Exception as e:
        print(f"[ERROR] Fallo al cargar las tablas de referencia en SQLite: {e}")
        raise