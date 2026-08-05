"""
Este es el archivo principal que arranca todo el programa. 
Básicamente es un script que llama a los demás archivos en orden:
1. Extrae los datos (extract.py)
2. Los limpia y cruza (transform.py)
3. Revisa que no la hayamos embarrado con los cálculos (validate.py)
4. Guarda los resultados (load.py)
5. Corre las consultas en SQL para ver los resultados finales (queries.py)

Para correr el proyecto solo tienes que ejecutar este archivo en la consola.
"""

from pathlib import Path
from extract import extract_all_transactions, extract_reference_data
from transform import profile_raw_data, print_profiling_report, clean_and_harmonize_data, transform_and_integrate_data
from validate import validate_integrated_data
from load import save_to_csv, load_to_sqlite, load_reference_tables
from queries import run_analytical_queries

def run_pipeline():
    """
    Ejecuta de principio a fin el Pipeline ETL.
    """
    print("\n" + "="*70)
    print("          STARTING RETAIL ANALYTICS ETL PIPELINE RUN")
    print("="*70)

    BASE_DIR = Path(__file__).resolve().parent.parent
    RAW_DIR = BASE_DIR / 'data' / 'raw'
    PROCESSED_CSV_PATH = BASE_DIR / 'data' / 'processed' / 'integrated_sales.csv'
    DB_PATH = BASE_DIR / 'database' / 'retail_analytics.db'

    # 1. EXTRACTION (Extracción)
    # Extraemos los datos crudos (raw) de las 3 ciudades y las tablas maestras.
    print("\n[STEP 1] Extracting raw transactions and reference tables...")
    df_raw = extract_all_transactions(RAW_DIR)
    ref_data = extract_reference_data(RAW_DIR)
    print(f" -> Extracted {len(df_raw)} raw transaction records.")

    # 2. PROFILING (Perfilamiento)
    # Analizamos los datos crudos para encontrar errores (nulos, duplicados, negativos).
    print("\n[STEP 2] Running data profiling on raw transactions...")
    profiling_summary = profile_raw_data(df_raw)
    print_profiling_report(profiling_summary)

    # 3. CLEANING & HARMONIZATION (Limpieza y Armonización)
    # Aplicamos reglas para limpiar los errores encontrados en el paso anterior.
    print("[STEP 3] Cleaning and harmonizing raw data...")
    df_clean = clean_and_harmonize_data(df_raw)
    print(f" -> Clean transactions remaining: {len(df_clean)} records.")

    # 4. TRANSFORMATION & INTEGRATION (Transformación)
    # Cruzamos (JOIN) las transacciones limpias con las tablas maestras para calcular ventas netas, brutas y descuentos.
    print("\n[STEP 4] Transforming and integrating with master tables...")
    df_integrated = transform_and_integrate_data(df_clean, ref_data)
    print(f" -> Integrated transactions ready: {len(df_integrated)} records.")

    # 4b. VALIDATION (Validación)
    # Verificamos matemáticamente que todo haya quedado bien cruzado (Quality Gate final).
    validate_integrated_data(df_integrated)

    # 5. LOADING (Carga de Datos)
    # Guardamos el resultado final en un archivo CSV y en la base de datos SQLite.
    print("\n[STEP 5] Persisting data to CSV and SQLite...")
    save_to_csv(df_integrated, PROCESSED_CSV_PATH)
    load_to_sqlite(df_integrated, DB_PATH)

    # 5b. CARGA DE TABLAS MAESTRAS (Para uso analítico)
    # Guardamos también las tablas de referencia (como metas mensuales) en la BD para poder hacer reportes SQL.
    print("\n[STEP 5b] Loading reference tables into SQLite for analytical queries...")
    load_reference_tables(ref_data, DB_PATH)

    # 6. QUERY & VERIFICATION (Consultas SQL)
    # Ejecutamos las consultas SQL finales para responder a los requerimientos de negocio (Lab 1A).
    print("\n[STEP 6] Executing Activity 11 analytical SQL queries...")
    run_analytical_queries(DB_PATH)

    print("="*70)
    print("          ETL PIPELINE RUN COMPLETED SUCCESSFULLY!")
    print("="*70 + "\n")

if __name__ == '__main__':
    run_pipeline()