"""
Module: main.py
Description: Main orchestration script that runs the end-to-end ETL pipeline for Lab 1B.
"""

from pathlib import Path
from extract import extract_all_transactions, extract_reference_data
from transform import profile_raw_data, print_profiling_report, clean_and_harmonize_data, transform_and_integrate_data
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

    # 1. EXTRACTION
    print("\n[STEP 1] Extracting raw transactions and reference tables...")
    df_raw = extract_all_transactions(RAW_DIR)
    ref_data = extract_reference_data(RAW_DIR)
    print(f" -> Extracted {len(df_raw)} raw transaction records.")

    # 2. PROFILING
    print("\n[STEP 2] Running data profiling on raw transactions...")
    profiling_summary = profile_raw_data(df_raw)
    print_profiling_report(profiling_summary)

    # 3. CLEANING & HARMONIZATION
    print("[STEP 3] Cleaning and harmonizing raw data...")
    df_clean = clean_and_harmonize_data(df_raw)
    print(f" -> Clean transactions remaining: {len(df_clean)} records.")

    # 4. TRANSFORMATION & INTEGRATION
    print("\n[STEP 4] Transforming, integrating with master tables, and running assertions...")
    df_integrated = transform_and_integrate_data(df_clean, ref_data)
    print(f" -> Integrated transactions ready: {len(df_integrated)} records.")

    # 5. LOADING
    print("\n[STEP 5] Persisting data to CSV and SQLite...")
    save_to_csv(df_integrated, PROCESSED_CSV_PATH)
    load_to_sqlite(df_integrated, DB_PATH)

    # Cargar tablas de referencia en SQLite (requerido para REQ 3 – monthly_targets JOIN)
    print("\n[STEP 5b] Loading reference tables into SQLite for analytical queries...")
    load_reference_tables(ref_data, DB_PATH)

    # 6. QUERY & VERIFICATION
    print("\n[STEP 6] Executing Activity 11 analytical SQL queries...")
    run_analytical_queries(DB_PATH)

    print("="*70)
    print("          ETL PIPELINE RUN COMPLETED SUCCESSFULLY!")
    print("="*70 + "\n")

if __name__ == '__main__':
    run_pipeline()