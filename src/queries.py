"""
Module: queries.py
Description: Executes SQL queries against the SQLite database (retail_analytics.db)
             to verify business requirements selected from Lab 1A.
"""

import sqlite3
import pandas as pd
from pathlib import Path

def run_analytical_queries(db_path: Path) -> None:
    """
    Se conecta a SQLite y ejecuta las consultas analíticas correspondientes 
    a los 6 requerimientos de negocio.
    """
    if not db_path.exists():
        print(f"[ERROR] La base de datos no existe en: {db_path}")
        return

    conn = sqlite3.connect(db_path)
    
    print("\n" + "="*70)
    print("         ANALYTICAL SQL QUERIES (BUSINESS REQUIREMENTS)")
    print("="*70)
    
    # Requerimiento 1: Total ventas por región y tienda
    q1 = """
    SELECT region, store_name, 
           SUM(quantity) AS total_units,
           ROUND(SUM(gross_sales), 2) AS total_gross_sales,
           ROUND(SUM(net_sales), 2) AS total_net_sales
    FROM sales_analytics
    GROUP BY region, store_name
    ORDER BY total_net_sales DESC;
    """
    print("\n--- Req 1: Total Revenue and Sales by Region/Store ---")
    print(pd.read_sql_query(q1, conn))

    # Requerimiento 2: Desempeño de ventas por categoría de producto
    q2 = """
    SELECT category, 
           SUM(quantity) AS units_sold,
           ROUND(SUM(net_sales), 2) AS total_net_sales
    FROM sales_analytics
    GROUP BY category
    ORDER BY total_net_sales DESC;
    """
    print("\n--- Req 2: Sales Performance by Product Category ---")
    print(pd.read_sql_query(q2, conn))

    # Requerimiento 3: Cumplimiento de metas mensuales por tienda
    q3 = """
    SELECT store_name, month, 
           ROUND(SUM(net_sales), 2) AS actual_net_sales
    FROM sales_analytics
    GROUP BY store_name, month
    ORDER BY store_name, month;
    """
    print("\n--- Req 3: Monthly Sales Target Achievement per Store ---")
    print(pd.read_sql_query(q3, conn))

    # Requerimiento 4: Tendencias temporales de ventas (Día de la semana)
    q4 = """
    SELECT day_name, 
           COUNT(sale_line_id) AS total_transactions,
           ROUND(SUM(net_sales), 2) AS total_net_sales
    FROM sales_analytics
    GROUP BY day_name
    ORDER BY total_net_sales DESC;
    """
    print("\n--- Req 4: Temporal Sales Trends by Day Name ---")
    print(pd.read_sql_query(q4, conn))

    # Requerimiento 5: Efectividad y uso de promociones
    q5 = """
    SELECT promotion_code, 
           COUNT(sale_line_id) AS total_applied,
           ROUND(SUM(discount_amount), 2) AS total_discount_given,
           ROUND(SUM(net_sales), 2) AS net_sales_generated
    FROM sales_analytics
    GROUP BY promotion_code
    ORDER BY total_discount_given DESC;
    """
    print("\n--- Req 5: Promotion Usage & Effectiveness ---")
    print(pd.read_sql_query(q5, conn))

    # Requerimiento 6: Consolidación por canal/fuente (Ciudad)
    q6 = """
    SELECT city, 
           COUNT(sale_line_id) AS total_records,
           ROUND(SUM(net_sales), 2) AS total_net_sales
    FROM sales_analytics
    GROUP BY city;
    """
    print("\n--- Req 6: Heterogeneous Data Consolidation Verification ---")
    print(pd.read_sql_query(q6, conn))
    
    print("\n" + "="*70 + "\n")
    conn.close()