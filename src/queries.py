"""
Aquí es donde respondemos las preguntas del negocio (el Lab 1A).
Nos conectamos a la base de datos de SQLite que creamos en el paso anterior y hacemos consultas en SQL para sacar:
- Cuánto se vendió cada mes y día.
- Cuáles fueron los productos y categorías más vendidos.
- Si las tiendas cumplieron o no con las metas del mes (cruzando ventas reales vs presupuesto).
- Si las campañas de descuento funcionaron y dejaron buen ROI.
Todo esto lo guardamos en tablas nuevas dentro de la misma base de datos para que sea fácil leerlas o graficarlas.
"""

import sqlite3
import pandas as pd
from pathlib import Path


def run_analytical_queries(db_path: Path) -> None:
    if not db_path.exists():
        print(f"[ERROR] La base de datos no existe en: {db_path}")
        return

    conn = sqlite3.connect(db_path)

    print("\n" + "=" * 70)
    print("     ACTIVITY 11 – VERIFICATION OF BUSINESS REQUIREMENTS")
    print("=" * 70)

    # ─────────────────────────────────────────────────────────────────────────
    # REQ 1: Daily Sales Aggregate + Monthly Trend
    # ─────────────────────────────────────────────────────────────────────────
    # Esta consulta agrupa las ventas por día y por tienda. 
    # Cuenta transacciones, suma unidades y calcula ventas brutas, descuentos y ventas netas.
    q1_daily = """
    SELECT
        sale_date                               AS date,
        store_name,
        city,
        region,
        COUNT(sale_line_id)                     AS total_transactions,
        SUM(quantity)                           AS total_units_sold,
        ROUND(SUM(gross_sales), 2)              AS total_gross_sales,
        ROUND(SUM(discount_amount), 2)          AS total_discounts,
        ROUND(SUM(net_sales), 2)                AS total_net_sales,
        ROUND(AVG(net_sales), 2)                AS avg_ticket
    FROM sales_analytics
    GROUP BY sale_date, store_name, city, region
    ORDER BY sale_date ASC, store_name ASC;
    """
    df_q1 = pd.read_sql_query(q1_daily, conn)
    df_q1.to_sql('REQ1_daily_sales_aggregate', conn, if_exists='replace', index=False)
    print("\n--- REQ 1: Daily Sales Aggregate ---")
    print(df_q1.to_string(index=False))

    # Esta consulta agrupa las ventas de forma MENSUAL.
    # Usa strftime('%Y-%m') para extraer el mes de la fecha de venta.
    q1_monthly = """
    SELECT
        strftime('%Y-%m', sale_date)            AS month,
        store_name,
        city,
        region,
        COUNT(sale_line_id)                     AS total_transactions,
        SUM(quantity)                           AS total_units_sold,
        ROUND(SUM(gross_sales), 2)              AS total_gross_sales,
        ROUND(SUM(net_sales), 2)                AS total_net_sales
    FROM sales_analytics
    GROUP BY strftime('%Y-%m', sale_date), store_name, city, region
    ORDER BY month ASC, store_name ASC;
    """
    df_q1m = pd.read_sql_query(q1_monthly, conn)
    df_q1m.to_sql('REQ1_monthly_trend', conn, if_exists='replace', index=False)
    print("\n--- REQ 1b: Monthly Revenue Trend (Seasonal View) ---")
    print(df_q1m.to_string(index=False))

    # ─────────────────────────────────────────────────────────────────────────
    # REQ 2: Category Performance + Product Breakdown
    # ─────────────────────────────────────────────────────────────────────────
    # Calcula el rendimiento por Categoria de Producto.
    # Además de sumar ventas, usa funciones de ventana (OVER) para calcular 
    # el porcentaje que representa cada categoría sobre el gran total y para asignar un ranking (RANK).
    q2_category = """
    SELECT
        category,
        COUNT(DISTINCT product_id)                              AS unique_products,
        COUNT(sale_line_id)                                     AS total_transactions,
        SUM(quantity)                                           AS total_units_sold,
        ROUND(SUM(gross_sales), 2)                              AS total_gross_sales,
        ROUND(SUM(discount_amount), 2)                          AS total_discounts,
        ROUND(SUM(net_sales), 2)                                AS total_net_sales,
        ROUND(AVG(net_sales), 2)                                AS avg_sale_per_transaction,
        ROUND(
            SUM(net_sales) * 100.0 / SUM(SUM(net_sales)) OVER (),
            2
        )                                                       AS pct_of_total_revenue,
        RANK() OVER (ORDER BY SUM(net_sales) DESC)              AS revenue_rank
    FROM sales_analytics
    GROUP BY category
    ORDER BY revenue_rank ASC;
    """
    df_q2 = pd.read_sql_query(q2_category, conn)
    df_q2.to_sql('REQ2_category_performance', conn, if_exists='replace', index=False)
    print("\n--- REQ 2: Sales Performance by Category ---")
    print(df_q2.to_string(index=False))

    # Calcula el rendimiento individual de cada PRODUCTO dentro de su categoría.
    # Usa PARTITION BY sa.category para rankear qué producto vende más dentro de su misma familia.
    q2_product = """
    SELECT
        sa.category,
        sa.product_id,
        p.product_name,
        SUM(sa.quantity)                                        AS units_sold,
        ROUND(SUM(sa.gross_sales), 2)                           AS gross_sales,
        ROUND(SUM(sa.net_sales), 2)                             AS net_sales,
        RANK() OVER (
            PARTITION BY sa.category
            ORDER BY SUM(sa.net_sales) DESC
        )                                                       AS rank_in_category
    FROM sales_analytics sa
    JOIN products p ON sa.product_id = p.product_id
    GROUP BY sa.category, sa.product_id, p.product_name
    ORDER BY sa.category, rank_in_category;
    """
    df_q2p = pd.read_sql_query(q2_product, conn)
    df_q2p.to_sql('REQ2_product_breakdown', conn, if_exists='replace', index=False)
    print("\n--- REQ 2b: Product Performance within Category ---")
    print(df_q2p.to_string(index=False))

    # ─────────────────────────────────────────────────────────────────────────
    # REQ 3: Table of Compliance Facts
    # ─────────────────────────────────────────────────────────────────────────
    # Cruza las ventas netas reales contra la tabla de METAS MENSUALES (monthly_targets).
    # Genera un estado ('ACHIEVED', 'NEAR TARGET', 'BELOW TARGET') usando un bloque CASE WHEN 
    # dependiendo de si superaron la meta, se acercaron (al 80%) o fracasaron.
    q3 = """
    SELECT
        st.store_name,
        st.city,
        st.region,
        mt.month                                                AS period,
        ROUND(COALESCE(SUM(sa.net_sales), 0), 2)               AS actual_net_sales,
        mt.sales_target                                         AS monthly_target,
        ROUND(
            COALESCE(SUM(sa.net_sales), 0) * 100.0 / mt.sales_target,
            2
        )                                                       AS compliance_pct,
        CASE
            WHEN COALESCE(SUM(sa.net_sales), 0) >= mt.sales_target
                THEN 'ACHIEVED'
            WHEN COALESCE(SUM(sa.net_sales), 0) >= mt.sales_target * 0.8
                THEN 'NEAR TARGET'
            ELSE 'BELOW TARGET'
        END                                                     AS compliance_status
    FROM monthly_targets mt
    JOIN stores st ON mt.store_id = st.store_id
    LEFT JOIN sales_analytics sa
        ON  sa.store_id = mt.store_id
        AND strftime('%Y-%m', sa.sale_date) = mt.month
    GROUP BY st.store_name, st.city, st.region, mt.month, mt.sales_target
    ORDER BY mt.month ASC, st.store_name ASC;
    """
    df_q3 = pd.read_sql_query(q3, conn)
    df_q3.to_sql('REQ3_compliance_facts', conn, if_exists='replace', index=False)
    print("\n--- REQ 3: Table of Compliance Facts ---")
    print(df_q3.to_string(index=False))

    # ─────────────────────────────────────────────────────────────────────────
    # REQ 4: Campaign Effectiveness + Sales Lift
    # ─────────────────────────────────────────────────────────────────────────
    # Mide la efectividad de las PROMOCIONES (Marketing).
    # Filtra las transacciones para que solo cuenten las que ocurrieron BETWEEN la fecha de inicio 
    # y la fecha de fin de la campaña promocional. Calcula el Retorno de Inversión (ROI).
    q4_effectiveness = """
    SELECT
        p.campaign_name,
        p.promotion_code,
        p.start_date                                            AS campaign_start,
        p.end_date                                              AS campaign_end,
        ROUND(p.discount_rate * 100, 1)                         AS discount_rate_pct,
        sa.category,
        COUNT(sa.sale_line_id)                                  AS total_transactions,
        SUM(sa.quantity)                                        AS total_units_sold,
        ROUND(SUM(sa.gross_sales), 2)                           AS total_gross_sales,
        ROUND(SUM(sa.discount_amount), 2)                       AS total_discount_cost,
        ROUND(SUM(sa.net_sales), 2)                             AS total_net_sales,
        ROUND(
            SUM(sa.net_sales) * 1.0 / NULLIF(SUM(sa.discount_amount), 0),
            2
        )                                                       AS revenue_per_discount_dollar,
        ROUND(
            (SUM(sa.net_sales) - SUM(sa.discount_amount))
            * 100.0 / NULLIF(SUM(sa.discount_amount), 0),
            2
        )                                                       AS roi_pct
    FROM promotions p
    JOIN sales_analytics sa
        ON  sa.promotion_code = p.promotion_code
        AND sa.sale_date BETWEEN p.start_date AND p.end_date
    GROUP BY p.campaign_name, p.promotion_code, p.start_date,
             p.end_date, p.discount_rate, sa.category
    ORDER BY roi_pct DESC, total_net_sales DESC;
    """
    df_q4a = pd.read_sql_query(q4_effectiveness, conn)
    df_q4a.to_sql('REQ4_campaign_effectiveness', conn, if_exists='replace', index=False)
    print("\n--- REQ 4a: Campaign Effectiveness (Revenue, Discount Cost & ROI) ---")
    print(df_q4a.to_string(index=False))

    print("\n" + "=" * 70)
    print("     ALL BUSINESS REQUIREMENTS VERIFIED SUCCESSFULLY")
    print("=" * 70 + "\n")

    conn.close()