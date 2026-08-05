"""
Módulo: validate.py

Descripción General:
Este módulo se encarga de la fase de Validación (Validate) del pipeline ETL. 
Actúa como la última compuerta de calidad (Quality Gate) antes de que los datos sean cargados a la base de datos.

Responsabilidades Clave:
1. Asegurar que las reglas de negocio críticas se hayan cumplido tras la transformación.
2. Comprobar la unicidad de las llaves primarias (ej. sale_line_id).
3. Verificar que no hayan quedado campos nulos tras los cruces (JOINs) con las tablas maestras.
4. Asegurar que las métricas financieras (ej. ventas netas) tengan sentido matemático (no negativas).
5. Lanzar un error crítico (AssertionError) que detenga el pipeline si los datos están corruptos.
"""

import pandas as pd

def validate_integrated_data(df: pd.DataFrame) -> None:
    """
    Ejecuta validaciones de calidad (assertions) sobre el DataFrame final integrado.
    Si alguna validación falla, el programa se detendrá automáticamente.
    
    Args:
        df (pd.DataFrame): DataFrame integrado y transformado listo para carga.
    """
    print("\n[VALIDATE] Ejecutando assertions de calidad de datos...")
    
    # 1. Unicidad de las llaves primarias
    assert df['sale_line_id'].is_unique, "[CRITICAL ERROR] sale_line_id contiene valores duplicados."
    
    # 2. Integridad de los cálculos financieros
    assert df['net_sales'].isnull().sum() == 0, "[CRITICAL ERROR] net_sales contiene valores nulos."
    assert (df['net_sales'] >= 0).all(), "[CRITICAL ERROR] net_sales contiene valores negativos."
    
    # 3. Éxito de los cruces (JOINs) con las tablas maestras
    assert df['store_name'].isnull().sum() == 0, "[WARNING/ERROR] Se detectó un store_id no mapeado tras el JOIN."
    assert df['product_name'].isnull().sum() == 0, "[WARNING/ERROR] Se detectó un product_id no mapeado tras el JOIN."
    
    print(" -> Todas las validaciones de calidad pasaron con éxito (Data is clean and robust).")
