# Resumen y Explicación de la Salida de Consola

A continuación documentamos la salida completa de la consola dividida por secciones. Agregamos una explicación en lenguaje natural seguida por el resultado exacto que arrojó nuestro sistema al ejecutarse.

## 1. El inicio y Perfilamiento de Datos
Lo primero que hace nuestro sistema es extraer los datos de las tres ciudades. En esta parte de la consola imprimimos un reporte para saber cuántos datos llegaron sucios (por ejemplo, 522 fechas mal escritas o 3 registros duplicados) y cuántos registros limpios logramos rescatar para trabajar.
```text
======================================================================
          STARTING RETAIL ANALYTICS ETL PIPELINE RUN
======================================================================

[STEP 1] Extracting raw transactions and reference tables...
  [EXTRACT] Cali CSV: 241 records loaded.
  [EXTRACT] Bogotá JSON: 281 records loaded.
  [EXTRACT] Medellín XML: 241 records loaded.
 -> Extracted 763 raw transaction records.

[STEP 2] Running data profiling on raw transactions...

==================================================
        PROFILING SUMMARY (RAW TRANSACTIONS)
==================================================
Total Raw Rows Ingested: 763

--- Missing Values per Column ---
  - sale_line_id: 0 nulls
  - sale_date: 0 nulls
  - store_id: 0 nulls
  - product_id: 0 nulls
  - quantity: 0 nulls
  - unit_price: 0 nulls
  - promotion_code: 717 nulls
  - payment_method: 0 nulls

--- Data Quality Issues Detected ---
  - Duplicate sale_line_ids : 3
  - Invalid/Null Quantities  : 2
  - Invalid/Null Prices      : 2
  - Invalid/Null Dates       : 522

--- Categorical Field Values ---
  - Distinct Store IDs       : ['S01', 'S02', 's02', 'S03']
  - Payment Methods          : ['Card', 'Cash', 'Transfer', ' card ', 'CASH']
==================================================

[STEP 3] Cleaning and harmonizing raw data...
 -> Clean transactions remaining: 755 records.

[STEP 4] Transforming and integrating with master tables...
 -> Integrated transactions ready: 755 records.

[VALIDATE] Ejecutando assertions de calidad de datos...
 -> Todas las validaciones de calidad pasaron con éxito (Data is clean and robust).

[STEP 5] Persisting data to CSV and SQLite...
[LOAD] Archivo CSV procesado guardado con éxito en: /Users/usuario/Desktop/Lab1B_ETL/data/processed/integrated_sales.csv
[LOAD] Carga a SQLite completada. Tabla 'sales_analytics' creada con 755 registros.

[STEP 5b] Loading reference tables into SQLite for analytical queries...
[LOAD] Tabla de referencia 'products' cargada con 15 registros.
[LOAD] Tabla de referencia 'stores' cargada con 3 registros.
[LOAD] Tabla de referencia 'promotions' cargada con 6 registros.
[LOAD] Tabla de referencia 'monthly_targets' cargada con 9 registros.

[STEP 6] Executing Activity 11 analytical SQL queries...

======================================================================
     ACTIVITY 11 – VERIFICATION OF BUSINESS REQUIREMENTS
======================================================================
```

## 2. El resumen de ventas diarias y mensuales (REQ 1)
Como ver las ventas por día es demasiada información, configuramos el programa para que también imprima un resumen por mes. Con esto podemos ver rápidamente que en Febrero, Marzo y Abril a las tres tiendas les fue bastante bien, moviendo millones cada mes de forma constante.
```text
--- REQ 1b: Monthly Revenue Trend (Seasonal View) ---
  month       store_name     city    region  total_transactions  total_units_sold  total_gross_sales  total_net_sales
2026-02    Bogotá Centro   Bogotá   Central                  97               140         21615000.0       21614342.0
2026-02       Cali Norte     Cali Southwest                  80               135         22940000.0       22939275.0
2026-02 Medellín Poblado Medellín Northwest                  77               109         18451000.0       18451000.0
2026-03    Bogotá Centro   Bogotá   Central                  87               127         19531000.0       19528115.4
2026-03       Cali Norte     Cali Southwest                  76               115         18383000.0       18381302.0
2026-03 Medellín Poblado Medellín Northwest                  91               145         23793000.0       23789704.2
2026-04    Bogotá Centro   Bogotá   Central                  94               135         21589000.0       21586720.0
2026-04       Cali Norte     Cali Southwest                  83               136         20632000.0       20629220.0
2026-04 Medellín Poblado Medellín Northwest                  70               104         15455000.0       15453340.0

```

## 3. El ranking de categorías y productos (REQ 2)
Luego, hacemos que la consola imprima qué tipo de productos son los que más dinero le dejan a nuestra empresa. Se puede observar que los pequeños electrodomésticos son los líderes indiscutibles en ventas. Además, programamos un detalle adicional para identificar exactamente qué producto específico se vendió más (como la freidora de aire).
```text
--- REQ 2: Sales Performance by Category ---
        category  unique_products  total_transactions  total_units_sold  total_gross_sales  total_discounts  total_net_sales  avg_sale_per_transaction  pct_of_total_revenue  revenue_rank
Small Appliances                4                 216               342         81680000.0           5695.0       81674305.0                 378121.78                 44.78             1
     Electronics                4                 190               280         47350000.0           4764.0       47345236.0                 249185.45                 25.96             2
   Home & Office                4                 244               360         30897000.0            662.4       30896337.6                 126624.33                 16.94             3
   Personal Care                3                 105               164         22462000.0           4860.0       22457140.0                 213877.52                 12.31             4

--- REQ 2b: Product Performance within Category ---
        category product_id         product_name  units_sold  gross_sales  net_sales  rank_in_category
     Electronics       P005  Wireless Headphones         101   22165000.0 22162096.0                 1
     Electronics       P007    Smartwatch Active          33   10230000.0 10228140.0                 2
     Electronics       P008        USB-C Charger         105    8190000.0  8190000.0                 3
     Electronics       P006    Bluetooth Speaker          41    6765000.0  6765000.0                 4
   Home & Office       P010      Ergonomic Mouse         111   12765000.0 12765000.0                 1
   Home & Office       P009        Desk Lamp LED         111   10212000.0 10211337.6                 2
   Home & Office       P011     Keyboard Compact          30    4140000.0  4140000.0                 3
   Home & Office       P012        Notebook Pack         108    3780000.0  3780000.0                 4
   Personal Care       P013           Hair Dryer         102   13770000.0 13765140.0                 1
   Personal Care       P014      Electric Shaver          30    5940000.0  5940000.0                 2
   Personal Care       P015        Digital Scale          32    2752000.0  2752000.0                 3
Small Appliances       P004         Air Fryer 4L          84   32760000.0 32755320.0                 1
Small Appliances       P003         Blender 500W         127   22225000.0 22225000.0                 2
Small Appliances       P002 Coffee Maker Premium          55   15675000.0 15675000.0                 3
Small Appliances       P001   Coffee Maker Basic          76   11020000.0 11018985.0                 4

[VIEWS] Creando Vistas Analíticas (SQL VIEWS) en la base de datos...
  -> Vista creada exitosamente: v_req1_daily_sales
  -> Vista creada exitosamente: v_req1_monthly_trend
  -> Vista creada exitosamente: v_req2_category_performance
  -> Vista creada exitosamente: v_req2_product_breakdown
  -> Vista creada exitosamente: v_req3_compliance_facts
  -> Vista creada exitosamente: v_req4_campaign_effectiveness

[ÉXITO] ¡Todas las Vistas SQL fueron creadas! Puedes consultarlas en tu DB.

Generando Gráfica REQ 1 (Tendencia de Ventas Mensuales por Tienda)...
Generando Gráfica REQ 2 (Desempeño por Categoría)...
Generando Gráfica REQ 3 (Cumplimiento de Metas)...
Generando Gráfica REQ 4 (Efectividad de Promociones)...

[ÉXITO] ¡Todas las gráficas fueron generadas exitosamente con alto nivel de detalle en '/Users/usuario/Desktop/Lab1B_ETL/images'!

```

## 4. La tabla de la verdad: ¿Cumplimos las metas? (REQ 3)
Esta parte la diseñamos pensando en los gerentes. Nuestro programa cruza las ventas netas reales de cada mes con la meta asignada. La consola imprime el porcentaje de cumplimiento y un estado. Por ejemplo, se nota que la sede de Cali logró su objetivo en Febrero, pero Medellín se quedó corto en Abril.
```text
--- REQ 3: Table of Compliance Facts ---
      store_name     city    region  period  actual_net_sales  monthly_target  compliance_pct compliance_status
   Bogotá Centro   Bogotá   Central 2026-02        21614342.0        23000000           93.98       NEAR TARGET
      Cali Norte     Cali Southwest 2026-02        22939275.0        19500000          117.64          ACHIEVED
Medellín Poblado Medellín Northwest 2026-02        18451000.0        20500000           90.00       NEAR TARGET
   Bogotá Centro   Bogotá   Central 2026-03        19528115.4        24000000           81.37       NEAR TARGET
      Cali Norte     Cali Southwest 2026-03        18381302.0        20500000           89.66       NEAR TARGET
Medellín Poblado Medellín Northwest 2026-03        23789704.2        21500000          110.65          ACHIEVED
   Bogotá Centro   Bogotá   Central 2026-04        21586720.0        25000000           86.35       NEAR TARGET
      Cali Norte     Cali Southwest 2026-04        20629220.0        21500000           95.95       NEAR TARGET
Medellín Poblado Medellín Northwest 2026-04        15453340.0        22500000           68.68      BELOW TARGET

[VIEWS] Creando Vistas Analíticas (SQL VIEWS) en la base de datos...
  -> Vista creada exitosamente: v_req1_daily_sales
  -> Vista creada exitosamente: v_req1_monthly_trend
  -> Vista creada exitosamente: v_req2_category_performance
  -> Vista creada exitosamente: v_req2_product_breakdown
  -> Vista creada exitosamente: v_req3_compliance_facts
  -> Vista creada exitosamente: v_req4_campaign_effectiveness

[ÉXITO] ¡Todas las Vistas SQL fueron creadas! Puedes consultarlas en tu DB.

Generando Gráfica REQ 1 (Tendencia de Ventas Mensuales por Tienda)...
Generando Gráfica REQ 2 (Desempeño por Categoría)...
Generando Gráfica REQ 3 (Cumplimiento de Metas)...
Generando Gráfica REQ 4 (Efectividad de Promociones)...

[ÉXITO] ¡Todas las gráficas fueron generadas exitosamente con alto nivel de detalle en '/Users/usuario/Desktop/Lab1B_ETL/images'!

```

## 5. ¿Funcionaron los descuentos? (REQ 4)
Aquí analizamos el impacto de las campañas de marketing. Nuestro algoritmo revisa cada promoción, calcula cuánto costó hacer el descuento y cuánto dinero retornó (el famoso ROI). La consola nos confirma que las campañas fueron bastante rentables.
```text
--- REQ 4a: Campaign Effectiveness (Revenue, Discount Cost & ROI) ---
      campaign_name promotion_code campaign_start campaign_end  discount_rate_pct         category  total_transactions  total_units_sold  total_gross_sales  total_discount_cost  total_net_sales  revenue_per_discount_dollar   roi_pct
        Home Office        PROMO08     2026-02-20   2026-03-10                8.0    Home & Office                   8                 9           828000.0                662.4         827337.6                      1249.00 124800.00
     Wearables Week       PROMO10B     2026-04-10   2026-04-30               10.0      Electronics                   5                 6          1860000.0               1860.0        1858140.0                       999.00  99800.00
        Coffee Week        PROMO10     2026-02-10   2026-02-28               10.0 Small Appliances                   4                 7          1015000.0               1015.0        1013985.0                       999.00  99800.00
     Audio Campaign        PROMO12     2026-03-15   2026-04-05               12.0      Electronics                   8                11          2420000.0               2904.0        2417096.0                       832.33  83133.33
       Kitchen Days        PROMO15     2026-03-01   2026-03-20               15.0 Small Appliances                   7                 8          3120000.0               4680.0        3115320.0                       665.67  66466.67
Personal Care Month        PROMO20     2026-04-01   2026-04-25               20.0    Personal Care                  12                18          2430000.0               4860.0        2425140.0                       499.00  49800.00

======================================================================
     ALL BUSINESS REQUIREMENTS VERIFIED SUCCESSFULLY
======================================================================

======================================================================
          ETL PIPELINE RUN COMPLETED SUCCESSFULLY!
======================================================================

[VIEWS] Creando Vistas Analíticas (SQL VIEWS) en la base de datos...
  -> Vista creada exitosamente: v_req1_daily_sales
  -> Vista creada exitosamente: v_req1_monthly_trend
  -> Vista creada exitosamente: v_req2_category_performance
  -> Vista creada exitosamente: v_req2_product_breakdown
  -> Vista creada exitosamente: v_req3_compliance_facts
  -> Vista creada exitosamente: v_req4_campaign_effectiveness

[ÉXITO] ¡Todas las Vistas SQL fueron creadas! Puedes consultarlas en tu DB.

Generando Gráfica REQ 1 (Tendencia de Ventas Mensuales por Tienda)...
Generando Gráfica REQ 2 (Desempeño por Categoría)...
Generando Gráfica REQ 3 (Cumplimiento de Metas)...
Generando Gráfica REQ 4 (Efectividad de Promociones)...

[ÉXITO] ¡Todas las gráficas fueron generadas exitosamente con alto nivel de detalle en '/Users/usuario/Desktop/Lab1B_ETL/images'!

```

## 6. Creación de Vistas y Gráficas
Al final, el sistema nos confirma que guardó toda esta información en la base de datos mediante la creación de vistas de SQL. Además, nos notifica que generó correctamente las cuatro gráficas en la carpeta de imágenes, dejando todo listo para la presentación.
```text
[VIEWS] Creando Vistas Analíticas (SQL VIEWS) en la base de datos...
  -> Vista creada exitosamente: v_req1_daily_sales
  -> Vista creada exitosamente: v_req1_monthly_trend
  -> Vista creada exitosamente: v_req2_category_performance
  -> Vista creada exitosamente: v_req2_product_breakdown
  -> Vista creada exitosamente: v_req3_compliance_facts
  -> Vista creada exitosamente: v_req4_campaign_effectiveness

[ÉXITO] ¡Todas las Vistas SQL fueron creadas! Puedes consultarlas en tu DB.

Generando Gráfica REQ 1 (Tendencia de Ventas Mensuales por Tienda)...
Generando Gráfica REQ 2 (Desempeño por Categoría)...
Generando Gráfica REQ 3 (Cumplimiento de Metas)...
Generando Gráfica REQ 4 (Efectividad de Promociones)...

[ÉXITO] ¡Todas las gráficas fueron generadas exitosamente con alto nivel de detalle en '/Users/usuario/Desktop/Lab1B_ETL/images'!

```
