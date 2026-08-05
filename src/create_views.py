"""
Módulo: create_views.py

Descripción General:
Este script se conecta a la base de datos `retail_analytics.db` y crea VISTAS SQL (VIEWS) 
apuntando a las tablas de resultados previamente generadas por el pipeline.
"""

import sqlite3
from pathlib import Path

def create_sql_views():
    BASE_DIR = Path(__file__).resolve().parent.parent
    DB_PATH = BASE_DIR / 'database' / 'retail_analytics.db'
    
    if not DB_PATH.exists():
        print(f"[ERROR] No se encontró la BD en {DB_PATH}. Corre main.py primero.")
        return
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("\n[VIEWS] Creando Vistas Analíticas (SQL VIEWS) en la base de datos...")
    
    views_to_create = {
        'v_req1_daily_sales': "SELECT * FROM REQ1_daily_sales_aggregate;",
        'v_req1_monthly_trend': "SELECT * FROM REQ1_monthly_trend;",
        'v_req2_category_performance': "SELECT * FROM REQ2_category_performance;",
        'v_req2_product_breakdown': "SELECT * FROM REQ2_product_breakdown;",
        'v_req3_compliance_facts': "SELECT * FROM REQ3_compliance_facts;",
        'v_req4_campaign_effectiveness': "SELECT * FROM REQ4_campaign_effectiveness;"
    }
    
    for view_name, select_query in views_to_create.items():
        cursor.execute(f"DROP VIEW IF EXISTS {view_name};")
        cursor.execute(f"CREATE VIEW {view_name} AS \n{select_query}")
        print(f"  -> Vista creada exitosamente: {view_name}")
        
    conn.commit()
    conn.close()
    
    print("\n[ÉXITO] ¡Todas las Vistas SQL fueron creadas! Puedes consultarlas en tu DB.\n")

if __name__ == "__main__":
    create_sql_views()
