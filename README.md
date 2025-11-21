# Pipeline ETL de Ordenes - Arquitectura Medallion

Pipeline ETL que extrae datos de ordenes desde la API http://ecommerce-haze-8597.fly.dev, los transforma usando una arquitectura Medallion (Bronze/Silver/Gold) con dbt, y los almacena en DuckDB. Orquestado con Apache Airflow en Docker.

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
├── docker-compose.yml
├── Dockerfile
├── Makefile                       # Comandos simplificados
├── requirements.txt
├── pyproject.toml
├── .env.example
└── README.md
```

## Requisitos Previos

- Docker y Docker Compose
- Python 3.11+
- uv (gestor de paquetes)
- Git
- make (para comandos simplificados)

### Instalacion de requisitos en Ubuntu/WSL
```bash
# Instalar make
sudo apt install make

# Instalar uv
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Despliegue del Proyecto

### 1. Clonar el repositorio
```bash
git clone https://github.com/agustingarcia210988/ecommerce-analytics.git
cd ecommerce-analytics
```

### 2. Configurar variables de entorno
```bash
cp .env.example .env
```

Editar `.env` con tu configuracion:
```env
# API
API_BASE_URL=http://ecommerce-haze-8597.fly.dev

# Postgres
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DB=

# Airflow
AIRFLOW_USER=
AIRFLOW_PASSWORD=
```

### 3. Crear carpetas necesarias
```bash
mkdir -p data logs
```

### 4. Levantar Airflow con Docker
```bash
make build
make up
```

O sin Makefile:
```bash
docker-compose build
docker-compose up -d
```

Verificar estado:
```bash
docker-compose ps
```

### 5. Acceder a Airflow

- URL: http://localhost:8080
- Usuario: valor de `AIRFLOW_USER` en `.env`
- Password: valor de `AIRFLOW_PASSWORD` en `.env`

### 6. Ejecutar el pipeline

**Ejecutar para una fecha especifica:**
```bash
make test
```

Para otra fecha:
```bash
docker-compose exec airflow-scheduler airflow dags test etl_ordenes_diario 2025-11-20
```

**Ejecutar para un rango de fechas (backfill):**
```bash
make backfill
```

**Ejecutar desde la UI de Airflow:**

1. Acceder a http://localhost:8080
2. Activar el DAG `etl_ordenes_diario`
3. Click en "Trigger DAG"

## Comandos disponibles (Makefile)

| Comando | Descripcion |
|---------|-------------|
| `make build` | Construye la imagen de Docker |
| `make up` | Inicia los contenedores |
| `make down` | Detiene los contenedores |
| `make restart` | Reinicia todo |
| `make logs` | Ver logs del scheduler |
| `make test` | Ejecuta el DAG para una fecha |
| `make backfill` | Ejecuta el DAG para un rango de fechas |
| `make clean` | Limpia logs y base de datos |
| `make pytest` | Ejecuta tests unitarios |

## Configuracion de Airflow Variables

El pipeline utiliza Airflow Variables para modificar su comportamiento sin cambiar codigo.

### Como configurar

1. Acceder a Airflow UI: http://localhost:8080
2. Ir a **Admin > Variables**
3. Click en **+** para agregar cada variable

### Variables disponibles

| Key | Valor default | Descripcion |
|-----|---------------|-------------|
| `api_url` | Valor de `API_BASE_URL` en `.env` | URL de la API de ordenes |
| `limite_ordenes` | `20` | Cantidad de ordenes a extraer por ejecucion |
| `solo_entregadas` | `true` | Si es `true`, filtra solo ordenes con status delivered |
| `dbt_target` | `dev` | Target de dbt a utilizar (dev/local) |
| `ejecutar_dbt_tests` | `true` | Si es `false`, omite la ejecucion de tests de dbt |

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
make pytest
```

O directamente:
```bash
uv run pytest tests/ -v
```

Resultado esperado:
```
tests/test_extraer.py::test_aplicar_transformaciones PASSED
tests/test_extraer.py::test_filtrar_ordenes_entregadas PASSED
tests/test_extraer.py::test_calcular_metricas PASSED
tests/test_extraer.py::test_calcular_metricas_dataframe_vacio PASSED

```

### Tests de dbt
```bash
cd ordenes_analytics
dbt test --profiles-dir .
```

## Consultar los Datos

**Importante:** Abrir la base de datos en modo read-only para evitar bloqueos mientras el pipeline corre.

### Desde DuckDB CLI
```bash
duckdb -readonly ordenes_analytics/ordenes.duckdb
```
```sql
-- Ver tablas disponibles
SHOW TABLES;

-- Consultar ventas diarias
SELECT * FROM gld_agg_ventas_diarias ORDER BY fecha;

-- Consultar fact de ventas
SELECT * FROM gld_fact_ventas LIMIT 10;

.quit
```

### Desde Python
```python
import duckdb

con = duckdb.connect('ordenes_analytics/ordenes.duckdb', read_only=True)
df = con.execute("SELECT * FROM gld_agg_ventas_diarias").df()
print(df)
con.close()
```

- **Python 3.11**: Lenguaje principal
- **pandas**: Transformacion de datos
- **Apache Airflow 2.x**: Orquestacion de pipelines
- **dbt**: Transformaciones SQL
- **DuckDB**: Data Warehouse OLAP
- **Docker**: Containerizacion
- **pytest**: Testing unitario
- **GitHub Actions**: CI/CD
- **uv**: Gestor de dependencias

Autor: Agustín García
