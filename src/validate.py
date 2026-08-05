"""
Este archivo funciona como una alarma de seguridad antes de guardar los datos.
Revisa un par de cosas básicas para asegurarnos de que la limpieza quedó bien:
- Que no haya IDs de ventas repetidos.
- Que no se nos haya colado ninguna venta neta negativa.
- Que al cruzar las tablas no hayan quedado productos o tiendas sin nombre (nulos).
Si encuentra algún error, detiene el programa de una para no guardar basura en la base de datos.
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
