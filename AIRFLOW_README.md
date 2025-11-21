# Airflow DAG - ETL de Órdenes

## Descripción del DAG

**Nombre**: `etl_ordenes_diario`

Este DAG ejecuta un pipeline ETL completo que:
1. Extrae órdenes de la API para la fecha de ejecución
2. Aplica transformaciones con pandas
3. Guarda en formato parquet
4. Ejecuta modelos dbt para crear tablas analíticas

## Configuración

```python
schedule_interval='0 2 * * *'  # Corre todos los días a las 2 AM
start_date=datetime(2024, 11, 1)
catchup=True  # ✅ Ejecuta fechas pasadas
```

## Características Importantes

### 🔄 Catchup = True
- Si el DAG falla un día, al correrlo después ejecuta TODAS las fechas que no se procesaron
- Ejemplo: Si falla el 15/11 y lo corres el 18/11, ejecutará el 15, 16, 17 y 18
- Usa `context['ds']` para obtener la fecha de cada ejecución

### 📅 Fecha de Ejecución
El DAG usa `context['ds']` (execution date) que Airflow pasa automáticamente:
- Formato: `YYYY-MM-DD`
- Es la fecha lógica de ejecución, no la fecha actual
- Permite procesar fechas pasadas si es necesario

### 🔗 Dependencias entre Tasks
```
extraer_ordenes >> ejecutar_dbt
```
- Primero extrae datos de la API
- Luego ejecuta dbt para transformar

## Tasks

### Task 1: extraer_ordenes
- Consulta la API con la fecha de ejecución
- Procesa y transforma datos con pandas
- Guarda en `data/ordenes_YYYY-MM-DD.parquet`
- Si falla, reintenta 1 vez después de 5 minutos

### Task 2: ejecutar_dbt
- Ejecuta `dbt run` 
- Lee todos los parquets en data/
- Crea tablas staging y marts en DuckDB
- Muestra resumen de resultados

## Acceso a la API desde Docker

⚠️ **Importante**: Para que Docker acceda a la API en localhost:

```python
url = f"http://ecommerce-haze-8597.fly.dev///orders?fecha={fecha_ejecucion}"
```

`host.docker.internal` permite al contenedor acceder al localhost del host.

## Cómo Probar

### 1. Backfill manual (ejecutar fechas pasadas)
```bash
docker-compose exec airflow-scheduler airflow dags backfill \
    -s 2024-11-01 \
    -e 2024-11-15 \
    etl_ordenes_diario
```

### 2. Ejecutar para una fecha específica
```bash
docker-compose exec airflow-scheduler airflow dags test \
    etl_ordenes_diario 2024-11-15
```

### 3. Trigger manual desde UI
- Ir a http://localhost:8080
- Click en el DAG `etl_ordenes_diario`
- Click en "Trigger DAG"

## Monitoreo

### Ver logs
```bash
# Logs del scheduler
docker-compose logs -f airflow-scheduler

# Logs de una task específica (desde Airflow UI)
# Click en el DAG → Grid → Click en task → Logs
```

### Verificar datos generados
```bash
# Ver parquets generados
ls -la data/

# Verificar tablas en DuckDB
python ver_tablas.py
```

## Troubleshooting

### Error: No se puede conectar a la API
- Verificá que la API esté corriendo en el host
- Asegurate de usar `host.docker.internal` en la URL

### Error: dbt command not found
- Necesitás instalar dbt en la imagen de Airflow
- Ver sección "Personalizar Imagen"

### DAG no aparece en Airflow
- Verificá que el archivo esté en `airflow/dags/`
- Esperá 1-2 minutos (Airflow escanea cada 30 segundos)
- Revisá logs: `docker-compose logs airflow-scheduler`

## Personalizar Imagen de Airflow

Si necesitás instalar dependencias (dbt, pandas, etc.):

**Crear `Dockerfile.airflow`**:
```dockerfile
FROM apache/airflow:2.8.1

USER root
RUN apt-get update && apt-get install -y git

USER airflow
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt
```

**Crear `requirements.txt`**:
```
dbt-duckdb>=1.7.0
pandas>=2.0.0
requests>=2.31.0
pyarrow>=14.0.0
duckdb>=0.9.0
```

**Actualizar `docker-compose.yml`**:
```yaml
# Cambiar:
image: apache/airflow:2.8.1

# Por:
build:
  context: .
  dockerfile: Dockerfile.airflow
```

Luego rebuild:
```bash
docker-compose build
docker-compose up -d
```
