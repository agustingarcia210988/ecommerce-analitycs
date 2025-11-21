# Pipeline ETL de Ordenes - Arquitectura Medallion

Pipeline ETL que extrae datos de ordenes desde una API, los transforma usando una arquitectura Medallion (Bronze/Silver/Gold) con dbt, y los almacena en DuckDB. Orquestado con Apache Airflow en Docker.

## Arquitectura del Pipeline
```
API REST --> Airflow DAG --> Extraccion (Python/Pandas) --> Parquet (Staging)
                                      |
                                      v
                            dbt (Bronze/Silver/Gold)
                                      |
                                      v
                                   DuckDB
```

## Modelo de Datos

### Diagrama del Modelo Estrella (Capa Gold)
```
                    +------------------+
                    |  slv_dim_fecha   |
                    +------------------+
                    | sk_fecha (PK)    |
                    | fecha            |
                    | anio             |
                    | mes              |
                    | mes_nombre       |
                    | dia              |
                    | dia_semana_nombre|
                    | tipo_dia         |
                    | trimestre        |
                    +------------------+
                            |
                            |
+------------------+        |        +------------------+
| gld_dim_cliente  |        |        | gld_dim_producto |
+------------------+        |        +------------------+
| sk_cliente (PK)  |        |        | sk_producto (PK) |
| id_cliente       |        |        | codigo_producto  |
| provincia_princ  |        |        | nombre_producto  |
| ciudad_principal |        |        | categoria        |
+------------------+        |        +------------------+
         |                  |                  |
         |                  |                  |
         +--------+---------+--------+---------+
                  |                  |
                  v                  v
           +------------------------------+
           |       gld_fact_ventas        |
           +------------------------------+
           | sk_venta (PK)                |
           | sk_orden (FK)                |
           | sk_cliente (FK)              |
           | sk_producto (FK)             |
           | sk_ubicacion (FK)            |
           | sk_fecha (FK)                |
           | id_orden                     |
           | cantidad                     |
           | precio_unitario              |
           | descuento_pct                |
           | total_item                   |
           | total_orden                  |
           +------------------------------+
                  |
                  |
         +--------+---------+
         |                  |
         v                  v
+------------------+  +---------------------+
|gld_dim_ubicacion |  | gld_agg_ventas_*    |
+------------------+  +---------------------+
| sk_ubicacion (PK)|  | Agregaciones por    |
| provincia        |  | dia y mes           |
| ciudad           |  +---------------------+
| codigo_postal    |
| region           |
+------------------+
```

### Capas del Modelo

| Capa | Descripcion | Modelos |
|------|-------------|---------|
| **Bronze** | Datos crudos sin transformar | `brz_ordenes`, `brz_items` |
| **Silver** | Datos limpios con surrogate keys | `slv_ordenes`, `slv_items`, `slv_dim_fecha` |
| **Gold** | Dimensiones, hechos y agregaciones | `gld_fact_ventas`, `gld_dim_*`, `gld_agg_*` |

## Estructura del Proyecto
```
ecommerce-analytics/
├── .github/
│   └── workflows/
│       └── tests.yml              # CI/CD con GitHub Actions
├── airflow/
│   └── dags/
│       └── dag_ordenes.py         # DAG principal
├── ordenes_analytics/             # Proyecto dbt
│   ├── dbt_project.yml
│   ├── profiles.yml
│   ├── macros/
│   │   └── date_dimensions.sql    # Macros para fechas y SKs
│   └── models/
│       ├── bronze/
│       ├── silver/
│       └── gold/
├── tests/
│   └── test_extraer.py            # Tests unitarios
├── data/                          # Archivos parquet generados
├── extraer_ordenes.py             # Script de extraccion
├── docker-compose.yml             # Configuracion de Airflow
├── Dockerfile                     # Imagen custom
├── requirements.txt
├── pyproject.toml
├── .gitignore
├── .env.example
└── README.md
```

## Requisitos Previos

- Docker y Docker Compose
- Python 3.11+
- uv (gestor de paquetes)
- Git

## Despliegue del Proyecto

### 1. Clonar el repositorio
```bash
git clone https://github.com/TU-USUARIO/ecommerce-analytics.git
cd ecommerce-analytics
```

### 2. Configurar variables de entorno
```bash
cp .env.example .env
```

### 3. Instalar dependencias Python
```bash
# Instalar uv si no lo tenes
curl -LsSf https://astral.sh/uv/install.sh | sh

# Instalar dependencias
uv sync
```

### 4. Crear carpetas necesarias
```bash
mkdir -p data logs airflow/logs
```

### 5. Levantar Airflow con Docker
```bash
# Build de la imagen
docker-compose build

# Iniciar servicios
docker-compose up -d

# Verificar estado
docker-compose ps
```

### 6. Acceder a Airflow

- URL: http://localhost:8080
- Usuario: `airflow`
- Password: `airflow`

### 7. Ejecutar el pipeline

1. En la UI de Airflow, activar el DAG `etl_ordenes_diario`
2. Click en "Trigger DAG"

O desde terminal:
```bash
docker-compose exec airflow-scheduler airflow dags backfill \
    etl_ordenes_diario \
    --start-date 2025-11-10 \
    --end-date 2025-11-20 \
    --reset-dagruns
```

## Flujo del Pipeline

### DAG: `etl_ordenes_diario`

| Task | Descripcion |
|------|-------------|
| `extraer_ordenes` | Extrae datos de la API, transforma con pandas, guarda en parquet |
| `ejecutar_dbt` | Ejecuta modelos dbt (Bronze -> Silver -> Gold) |
| `ejecutar_dbt_tests` | Ejecuta tests de calidad de datos en dbt |

### Transformaciones Aplicadas

**En Python/Pandas:**
- Conversion de fecha a datetime
- Calculo de porcentaje de descuento
- Calculo de precio promedio por item
- Limpieza de direcciones vacias
- Filtrado de ordenes entregadas (status = delivered)

**En dbt:**
- Bronze: Ingesta de datos crudos desde parquet
- Silver: Limpieza, normalizacion, generacion de surrogate keys
- Gold: Creacion de dimensiones, tabla de hechos y agregaciones

## Tests

### Ejecutar tests unitarios
```bash
uv run pytest tests/ -v
```

### Tests implementados

- `test_aplicar_transformaciones`: Verifica transformaciones de datos
- `test_filtrar_ordenes_entregadas`: Verifica filtrado por estado
- `test_calcular_metricas`: Verifica calculo de metricas agregadas
- `test_calcular_metricas_dataframe_vacio`: Verifica manejo de datos vacios

### Tests de dbt
```bash
cd ordenes_analytics
dbt test --profiles-dir .
```

## Consultar los Datos

### Desde DuckDB CLI
```bash
duckdb ordenes_analytics/ordenes.duckdb

-- Ver tablas disponibles
SHOW TABLES;

-- Consultar ventas diarias
SELECT * FROM gld_agg_ventas_diarias ORDER BY fecha;

-- Consultar ventas mensuales
SELECT * FROM gld_agg_ventas_mensuales;

-- Consultar fact de ventas
SELECT * FROM gld_fact_ventas LIMIT 10;

.quit
```

### Desde Python
```python
import duckdb

con = duckdb.connect('ordenes_analytics/ordenes.duckdb')
df = con.execute("SELECT * FROM gld_agg_ventas_diarias").df()
print(df)
con.close()
```

## Comandos Utiles

### Docker
```bash
# Ver logs
docker-compose logs -f airflow-scheduler

# Reiniciar servicios
docker-compose restart

# Parar todo
docker-compose down

# Rebuild completo
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### dbt
```bash
cd ordenes_analytics

# Ejecutar todos los modelos
dbt run --profiles-dir .

# Ejecutar solo una capa
dbt run --profiles-dir . --select bronze
dbt run --profiles-dir . --select silver
dbt run --profiles-dir . --select gold

# Ejecutar tests
dbt test --profiles-dir .

# Generar documentacion
dbt docs generate --profiles-dir .


## Tecnologias Utilizadas

- **Python 3.11**: Lenguaje principal
- **pandas**: Transformacion de datos
- **Apache Airflow 2.x**: Orquestacion de pipelines
- **dbt**: Transformaciones SQL
- **DuckDB**: Data Warehouse OLAP
- **Docker**: Containerizacion
- **pytest**: Testing unitario
- **GitHub Actions**: CI/CD
- **uv**: Gestor de dependencias

## Autor

Agustin Garcia