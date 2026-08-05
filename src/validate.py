"""
Validación de calidad

Este archivo sirve para revisar que los datos hayan quedado perfectos antes de guardarlos. Nos aseguramos de que no existan ventas duplicadas y verificamos que los cálculos matemáticos de las ventas netas no hayan dado números negativos. También confirmamos que todos los productos y tiendas tengan su nombre correcto y no hayan quedado vacíos. Si encuentra algún error grave en la información, detiene el programa automáticamente para no dañar la base de datos.
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
