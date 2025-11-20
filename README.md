# Pipeline ETL de Órdenes - Data Engineering

Pipeline completo de ETL que extrae datos de órdenes desde una API, los transforma con pandas y dbt, y los carga a DuckDB. Orquestado con Apache Airflow en Docker.

## 🏗️ Arquitectura

```
API (FastAPI) → Airflow DAG → Extracción (Python/pandas) → Parquet → 
dbt (DuckDB) → Tablas Analíticas
```

## 📁 Estructura del Proyecto

```
proyecto-ordenes/
├── api_ordenes.py              # API de órdenes (datos sintéticos)
├── extraer_ordenes.py          # Script de extracción standalone
├── docker-compose.yml          # Airflow + Postgres
├── Dockerfile                  # Imagen custom de Airflow
├── requirements.txt            # Dependencias Python
├── airflow/
│   └── dags/
│       └── dag_ordenes.py     # DAG principal de ETL
├── ordenes_analytics/          # Proyecto dbt
│   ├── dbt_project.yml
│   ├── profiles.yml
│   └── models/
│       ├── staging/
│       │   └── stg_ordenes.sql
│       └── marts/
│           └── mart_resumen_ventas.sql
├── data/                       # Archivos parquet generados
└── tests/
    └── test_extraer.py        # Tests unitarios
```

## 🚀 Inicio Rápido

### 1. Instalar dependencias

```bash
uv sync
```

### 2. Iniciar la API de órdenes

```bash
# En una terminal
uv run python api_ordenes.py
```

La API estará disponible en `http://localhost:8000`

### 3. Levantar Airflow con Docker

```bash
# Build de la imagen
docker-compose build

# Iniciar servicios
docker-compose up -d

# Verificar que estén corriendo
docker-compose ps
```

Acceder a Airflow UI: `http://localhost:8080`
- Usuario: `airflow`
- Password: `airflow`

### 4. Ejecutar el pipeline

**Opción A: Desde Airflow UI**
1. Ir a `http://localhost:8080`
2. Activar el DAG `etl_ordenes_diario`
3. Click en "Trigger DAG"

**Opción B: Desde terminal**
```bash
docker-compose exec airflow-scheduler airflow dags test etl_ordenes_diario 2024-11-15
```

**Opción C: Script standalone (sin Airflow)**
```bash
uv run python extraer_ordenes.py
```

## 🔄 Flujo del Pipeline

### DAG de Airflow: `etl_ordenes_diario`

**Task 1: `extraer_ordenes`**
- Consulta API: `GET /orders?fecha={execution_date}`
- Procesa con pandas (transformaciones)
- Filtra órdenes `delivered`
- Guarda en: `data/ordenes_YYYY-MM-DD.parquet`

**Task 2: `ejecutar_dbt`**
- Lee parquets desde `data/`
- Crea tabla staging: `stg_ordenes`
- Crea tabla marts: `mart_resumen_ventas`
- Almacena en DuckDB: `ordenes_analytics/ordenes.duckdb`

### Transformaciones aplicadas

En **pandas**:
- Conversión de fecha a datetime
- Cálculo de porcentaje de descuento
- Precio promedio por ítem
- Limpieza de direcciones vacías

En **dbt**:
- Staging: Filtrado y limpieza
- Marts: Agregaciones por categoría

## 🧪 Tests

```bash
# Ejecutar tests unitarios
uv run pytest tests/ -v

# Tests específicos
uv run pytest tests/test_extraer.py::test_aplicar_transformaciones -v
```

Tests incluidos:
- ✅ Procesamiento de órdenes
- ✅ Transformaciones de datos
- ✅ Cálculo de métricas
- ✅ Estructura de DataFrames

## 📊 Ver los Datos

### DuckDB CLI

```bash
# Abrir la base de datos
duckdb ordenes_analytics/ordenes.duckdb

# Dentro de DuckDB
SHOW TABLES;
SELECT * FROM stg_ordenes LIMIT 5;
SELECT * FROM mart_resumen_ventas;
.quit
```

### Con Python

```bash
cat > ver_datos.py << 'EOF'
import duckdb
con = duckdb.connect('ordenes_analytics/ordenes.duckdb')
print(con.execute("SELECT * FROM mart_resumen_ventas").df())
con.close()
EOF

uv run python ver_datos.py
```

### DBeaver (UI Gráfica)

1. Descargar DBeaver: https://dbeaver.io/download/
2. Nueva conexión → DuckDB
3. Path: `ordenes_analytics/ordenes.duckdb`
4. Explorar tablas visualmente

## 🔧 Configuración

### Variables de entorno (opcional)

Crear `.env` en la raíz:
```bash
API_BASE_URL=http://localhost:8000
AIRFLOW_UID=50000
```

### Configuración del DAG

En `airflow/dags/dag_ordenes.py`:
- **Schedule**: `0 2 * * *` (diario a las 2 AM)
- **Start date**: `2024-11-01`
- **Catchup**: `True` (ejecuta fechas pasadas si falla)

## 📝 API de Órdenes

La API genera datos sintéticos reproducibles (misma fecha = mismos datos).

**Endpoints:**
```bash
# Raíz
GET http://localhost:8000/

# Obtener órdenes por fecha
GET http://localhost:8000/orders?fecha=2024-11-15
```

**Características:**
- Genera 3-10 órdenes por día
- 8 productos diferentes
- 5 estados posibles
- Datos reproducibles (usa fecha como seed)

## 🐳 Docker

### Comandos útiles

```bash
# Ver logs
docker-compose logs -f airflow-scheduler

# Reiniciar servicios
docker-compose restart

# Parar todo
docker-compose down

# Limpiar todo (incluye volúmenes)
docker-compose down -v
```

### Rebuild después de cambios

```bash
docker-compose build --no-cache
docker-compose up -d
```

## 🛠️ Tecnologías

- **Python 3.11**: Lenguaje principal
- **pandas**: Transformación de datos
- **FastAPI**: API de órdenes
- **Apache Airflow 2.8**: Orquestación
- **dbt 1.7**: Transformaciones SQL
- **DuckDB**: Data Warehouse OLAP
- **Docker**: Containerización
- **pytest**: Testing

## 📂 Datos Generados

### Archivos Parquet
- Ubicación: `data/ordenes_YYYY-MM-DD.parquet`
- Formato: Parquet (columnar)
- Contiene: Órdenes delivered con transformaciones

### Tablas en DuckDB

**stg_ordenes**
- Órdenes filtradas y limpias
- Todas las columnas originales + transformaciones
- Materializadas como tabla

**mart_resumen_ventas**
- Agregaciones por categoría
- Métricas: cantidad, totales, promedios
- Optimizada para análisis

## 🔍 Troubleshooting

**Error: API no responde**
```bash
# Verificar que la API esté corriendo
curl http://localhost:8000/
```

**Error: DAG no aparece en Airflow**
```bash
# Ver logs del scheduler
docker-compose logs -f airflow-scheduler

# Verificar que el archivo esté en airflow/dags/
ls -la airflow/dags/dag_ordenes.py
```

**Error: dbt profile not found**
```bash
# Verificar que profiles.yml exista
cat ordenes_analytics/profiles.yml
```

**Error: No files found (parquet)**
- Verificar que la ruta en `stg_ordenes.sql` sea correcta
- Debe ser: `/opt/airflow/data/ordenes_*.parquet`

## 🎯 Próximos Pasos

Para completar el TP:
1. ✅ Pipeline ETL funcionando
2. ✅ Tests unitarios
3. ✅ Docker + Airflow
4. ⬜ GitHub Actions (CI/CD)
5. ⬜ Conexión a Redshift
6. ⬜ Documentación final

## 📄 Licencia

Proyecto educativo - ITBA Cloud Data Engineering