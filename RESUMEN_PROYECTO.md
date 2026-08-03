# Resumen y Explicación del Proyecto ETL (Laboratorio 1B)

## 1. Contexto del Proyecto

Este proyecto es la **segunda parte (Lab 1B)** de un caso de estudio sobre analítica de retail. En el **Lab 1A**, se definieron los requerimientos de negocio y las preguntas que la empresa necesitaba responder. En este **Lab 1B**, el objetivo es construir un **Pipeline ETL (Extract, Transform, Load)** completo y automatizado para ingerir datos heterogéneos, procesarlos y dejarlos listos para responder a dichas preguntas de negocio.

Se construyó un sistema modular en Python siguiendo buenas prácticas de ingeniería de datos y dividido en etapas bien definidas.

---

## 2. Arquitectura del Sistema (Pipeline ETL)

El pipeline está compuesto por los siguientes bloques, orquestados desde `src/main.py`:

1. **Extract (Extracción)**: Lectura de fuentes crudas (CSV, JSON, XML) sin alterar su contenido.
2. **Profile (Perfilamiento)**: Análisis de calidad de datos para identificar nulos, duplicados y anomalías.
3. **Clean & Harmonize (Limpieza)**: Estandarización de datos, tipos y eliminación de errores basándose en el perfilamiento.
4. **Transform & Integrate (Transformación)**: Cruces (JOINs) con tablas maestras y cálculo de métricas financieras.
5. **Load (Carga)**: Persistencia de los datos limpios en un archivo CSV y en una base de datos relacional SQLite.
6. **Query (Análisis)**: Ejecución de consultas SQL para validar los requerimientos del negocio.

---

## 3. Resumen de lo que Implementaste (Explicación por Archivos)

A continuación se detalla cómo resolviste cada actividad de las instrucciones del laboratorio en tu código:

### `src/extract.py` (Actividad 3)
* **Lo que hiciste**: Escribiste funciones individuales para leer ventas de tres ciudades en formatos distintos: `sales_cali.csv`, `sales_bogota.json` y `sales_medellin.xml`. Además, extrajiste las tablas de referencia (`products`, `stores`, etc.).
* **Por qué es importante**: El código lleva todos los formatos heterogéneos a una estructura en común de pandas (`COMMON_TRANSACTION_COLUMNS`), cumpliendo la regla estricta de **no hacer transformaciones de negocio aquí**, solo ingestar los datos.

### `src/transform.py` (Actividades 4, 5, 6 y 7)
Este es el núcleo de tu procesamiento y está dividido en tres funciones clave:
* **`profile_raw_data()`**: Escanea las transacciones y cuenta nulos, duplicados, cantidades o fechas inválidas. Esto te permite tomar decisiones de limpieza basadas en evidencia.
* **`clean_and_harmonize_data()`**: Limpia los espacios en blanco, estandariza mayúsculas/minúsculas, convierte textos a números (y fechas a tipo `datetime`), rellena códigos de promoción vacíos con `'NONE'` y, lo más importante, **filtra los registros malos** (cantidades/precios $\le 0$).
* **`transform_and_integrate_data()`**: Hace el cruce (*merge/JOIN*) con las tablas maestras de productos, tiendas y promociones. Además, aquí se calculan las métricas clave de negocio que no venían en los datos originales:
    * $\text{gross\_sales} = \text{quantity} \times \text{unit\_price}$
    * $\text{discount\_amount} = \text{gross\_sales} \times (\text{discount\_rate} / 100)$
    * $\text{net\_sales} = \text{gross\_sales} - \text{discount\_amount}$

### `src/load.py` (Actividad 8)
* **Lo que hiciste**: Construiste dos funciones, `save_to_csv` y `load_to_sqlite`.
* **Por qué es importante**: Garantiza que el trabajo de limpieza no se pierda. El CSV (`data/processed/integrated_sales.csv`) sirve como respaldo plano, mientras que SQLite (`database/retail_analytics.db`) permite que los analistas o herramientas de BI consulten los datos de forma relacional. Al usar `if_exists='replace'`, lograste que tu pipeline sea **idempotente** (se puede ejecutar múltiples veces sin duplicar datos).

### `src/queries.py` (Actividad 9)
* **Lo que hiciste**: Conectaste Python a la base de datos SQLite recién generada y escribiste 6 consultas SQL (`q1` a `q6`).
* **Por qué es importante**: Cada consulta responde directamente a un requerimiento de negocio del Lab 1A, como por ejemplo: "Total de ventas por región y tienda" o "Desempeño de ventas por categoría". Esto demuestra que el ETL sí cumple su propósito comercial.

### `src/main.py` (Actividad 10)
* **Lo que hiciste**: Es el orquestador principal. Importa todas las funciones de los otros archivos y las ejecuta secuencialmente, imprimiendo logs en la terminal para indicar el progreso.

---

## 4. Conclusión y Reflexión

Tu trabajo demuestra una transición exitosa de "pensar en requerimientos" (Lab 1A) a "construir el sistema que los resuelve" (Lab 1B). 
* Lograste **desacoplar** la extracción, de la transformación y de la carga. Si mañana Medellín cambia su formato de XML a JSON, **solo tienes que modificar `extract.py`**, el resto del pipeline seguirá funcionando intacto.
* Al aplicar validaciones de calidad (quitando números negativos o duplicados), garantizas que los reportes de `queries.py` muestren información financiera real y confiable, evitando tomar malas decisiones de negocio.

---

## 5. Matriz de Estado del Proyecto (Laboratorio 1B)

| Componente / Archivo | Estado | Responsable | Descripción / Estado Actual |
| :--- | :--- | :--- | :--- |
| **`README.md`** | 🟢 Completado | Michael | Documentación modular, arquitectura, matriz de profiling y guía de ejecución. |
| **`src/extract.py`** | 🟢 Completado | Michael | Ingesta de fuentes heterogéneas (CSV, JSON, XML) y tablas de referencia. |
| **`src/transform.py`**| 🟢 Completado | Michael | Profiling, limpieza de nulos/duplicados/errores, JOINs y cálculo de métricas financieras. |
| **`src/load.py`** | 🟢 Completado | Michael | Exportación a CSV procesado y persistencia a SQLite (`retail_analytics.db`). |
| **`src/queries.py`** | 🟢 Completado | Michael | 6 consultas SQL analíticas para verificar los requerimientos de negocio de Lab 1A. |
| **`src/main.py`** | 🟢 Completado | Michael | Orquestador ejecutable end-to-end del pipeline. |
| **Validación Local** | 🟡 Pendiente Equipo | Grupo | Clonar/actualizar repo y ejecutar `python src/main.py` en sus entornos locales. |
| **Revisión de Rúbrica** | 🟡 Pendiente Equipo | Grupo | Comparar los outputs obtenidos en consola contra la guía de evaluación del profesor. |
| **Entrega Final** | 🟡 Pendiente Equipo | Grupo | Preparar entregable final (reporte/video/zip según pida el profesor) y subir a la plataforma. |

---

## 6. Próximos Pasos para el Grupo (¿Qué deben hacer ahora?)

Como el Pipeline ETL y la arquitectura modular ya están 100% desarrollados y subidos al repositorio, los siguientes pasos para el grupo son:

1. **Sincronizar el repositorio local**:
   Ejecuten en su terminal:
   ```bash
   git pull origin main
Ejecutar y probar el pipeline:
Asegúrense de tener Python 3.9+ y pandas instalados, y corran el orquestador:

Bash
python src/main.py
Verifiquen que les genere la carpeta data/processed/, la base de datos database/retail_analytics.db y les imprima en consola las tablas SQL de los 6 requerimientos.

Revisión final de entregables:

Confirmar si la rúbrica del laboratorio exige entregar algún informe escrito adicional, presentación o video de explicación.

Cualquier mejora o ajuste que deseen realizar en los scripts pueden subirlo directamente haciendo git add, git commit y git push origin main (todos tienen acceso de escritura directa al repositorio).