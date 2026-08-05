"""
Generación de gráficas

Aquí leemos la base de datos para crear las gráficas visuales del proyecto. Generamos gráficas para ver la tendencia de ventas a lo largo de los meses por cada tienda, el desempeño de las categorías de productos, la comparación de las metas contra las ventas reales y el impacto de las campañas promocionales. Todas las gráficas se guardan automáticamente en una carpeta y les agregamos los valores exactos encima de las barras para que sean muy fáciles de leer.
"""

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

def generate_visualizations():
    BASE_DIR = Path(__file__).resolve().parent.parent
    DB_PATH = BASE_DIR / 'database' / 'retail_analytics.db'
    IMG_DIR = BASE_DIR / 'images'
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    
    if not DB_PATH.exists():
        print(f"[ERROR] No se encontró la base de datos en {DB_PATH}. Corre main.py primero.")
        return
        
    conn = sqlite3.connect(DB_PATH)
    
    # Estilo general
    sns.set_theme(style="whitegrid")
    
    # ---------------------------------------------------------
    # REQ 1: Tendencia de Ventas Mensuales (Gráfico de Líneas)
    # ---------------------------------------------------------
    print("Generando Gráfica REQ 1 (Tendencia de Ventas Mensuales por Tienda)...")
    # Extraemos el total por mes y por tienda
    df_req1 = pd.read_sql_query("SELECT month, store_name, total_net_sales FROM REQ1_monthly_trend ORDER BY month", conn)
    
    plt.figure(figsize=(10, 6))
    # Al poner hue='store_name', Seaborn dibuja automáticamente una línea de distinto color por cada sucursal
    ax = sns.lineplot(data=df_req1, x='month', y='total_net_sales', hue='store_name', marker='o', linewidth=3, markersize=10, palette='Set1')
    
    plt.title('REQ 1: Evolución de Ventas Netas por Sucursal\n(Análisis del 1er Trimestre - Q1 2026)', fontsize=16, fontweight='bold', pad=15)
    plt.xlabel('Mes del Año', fontsize=13)
    plt.ylabel('Ventas Netas ($)', fontsize=13)
    
    # Etiquetas de datos para cada punto (ajustado para que no se traslapen)
    for line_idx in range(len(ax.lines)):
        # Iterar sobre los puntos x, y de cada línea trazada
        for x, y in zip(ax.lines[line_idx].get_xdata(), ax.lines[line_idx].get_ydata()):
            if not pd.isna(y):
                plt.text(x, y + 500000, f"${y/1000000:.1f}M", ha='center', va='bottom', fontsize=9, fontweight='bold', color='gray')
    
    # Ajustar la leyenda
    plt.legend(title='Sucursal', fontsize=11, title_fontsize=12)
    plt.tight_layout()
    plt.savefig(IMG_DIR / 'req1_monthly_trend.png', dpi=300)
    plt.close()
    
    # ---------------------------------------------------------
    # REQ 2: Ventas por Categoría (Gráfico de Barras)
    # ---------------------------------------------------------
    print("Generando Gráfica REQ 2 (Desempeño por Categoría)...")
    df_req2 = pd.read_sql_query("SELECT category, total_net_sales FROM REQ2_category_performance ORDER BY total_net_sales DESC", conn)
    
    plt.figure(figsize=(10, 6))
    ax = sns.barplot(data=df_req2, x='category', y='total_net_sales', hue='category', palette='viridis', legend=False)
    
    plt.title('REQ 2: Desempeño y Rentabilidad por Categoría de Producto\n(Ranking de Mayor a Menor Ventas)', fontsize=16, fontweight='bold', pad=15)
    plt.xlabel('Categoría de Producto', fontsize=13)
    plt.ylabel('Ventas Netas Acumuladas ($)', fontsize=13)
    
    # Etiquetas de datos
    for p in ax.patches:
        ax.annotate(f"${p.get_height():,.0f}", (p.get_x() + p.get_width() / 2., p.get_height()), ha='center', va='center', xytext=(0, 10), textcoords='offset points', fontsize=11, fontweight='bold')
        
    plt.tight_layout()
    plt.savefig(IMG_DIR / 'req2_category_performance.png', dpi=300)
    plt.close()

    # ---------------------------------------------------------
    # REQ 3: Cumplimiento de Metas por Tienda (Gráfico de Barras Agrupadas)
    # ---------------------------------------------------------
    print("Generando Gráfica REQ 3 (Cumplimiento de Metas)...")
    df_req3 = pd.read_sql_query("SELECT store_name, SUM(actual_net_sales) as actual_sales, SUM(monthly_target) as target FROM REQ3_compliance_facts GROUP BY store_name", conn)
    df_req3_melted = pd.melt(df_req3, id_vars=['store_name'], value_vars=['actual_sales', 'target'], var_name='Metric', value_name='Amount')
    
    # Mapeo de nombres para la leyenda
    df_req3_melted['Metric'] = df_req3_melted['Metric'].map({'actual_sales': 'Ventas Reales', 'target': 'Presupuesto/Meta'})
    
    plt.figure(figsize=(12, 7))
    ax = sns.barplot(data=df_req3_melted, x='store_name', y='Amount', hue='Metric', palette=['#3498DB', '#E74C3C'])
    
    plt.title('REQ 3: Evaluación de Cumplimiento de Metas por Sucursal\n(Ventas Reales vs. Presupuesto Asignado)', fontsize=16, fontweight='bold', pad=15)
    plt.xlabel('Sucursal (Tienda)', fontsize=13)
    plt.ylabel('Monto en Dinero ($)', fontsize=13)
    plt.legend(title='Indicador Financiero', fontsize=11, title_fontsize=12)
    
    # Etiquetas de datos
    for p in ax.patches:
        ax.annotate(f"${p.get_height()/1000000:.1f}M", (p.get_x() + p.get_width() / 2., p.get_height()), ha='center', va='center', xytext=(0, 10), textcoords='offset points', fontsize=10, fontweight='bold')
        
    plt.tight_layout()
    plt.savefig(IMG_DIR / 'req3_compliance_targets.png', dpi=300)
    plt.close()

    # ---------------------------------------------------------
    # REQ 4: ROI de Campañas Promocionales (Gráfico Horizontal)
    # ---------------------------------------------------------
    print("Generando Gráfica REQ 4 (Efectividad de Promociones)...")
    df_req4 = pd.read_sql_query("SELECT campaign_name, roi_pct FROM REQ4_campaign_effectiveness ORDER BY roi_pct ASC", conn)
    
    plt.figure(figsize=(10, 6))
    ax = sns.barplot(data=df_req4, y='campaign_name', x='roi_pct', hue='campaign_name', palette='magma', legend=False)
    
    plt.title('REQ 4: Efectividad (ROI %) por Campaña Promocional\n(Mide el Retorno de Inversión por cada dólar descontado)', fontsize=16, fontweight='bold', pad=15)
    plt.xlabel('Retorno de Inversión - ROI (%)', fontsize=13)
    plt.ylabel('Campaña de Marketing', fontsize=13)
    
    # Etiquetas de datos (Horizontal)
    for p in ax.patches:
        width = p.get_width()
        plt.text(width + (width*0.02), p.get_y() + p.get_height()/2., f"{width:,.0f}%", ha='left', va='center', fontsize=11, fontweight='bold')
        
    plt.tight_layout()
    plt.savefig(IMG_DIR / 'req4_campaign_roi.png', dpi=300)
    plt.close()

    conn.close()
    print(f"\n[ÉXITO] ¡Todas las gráficas fueron generadas exitosamente con alto nivel de detalle en '{IMG_DIR}'!")

if __name__ == "__main__":
    generate_visualizations()
