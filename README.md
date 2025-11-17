# Proyecto de Extracción de Órdenes

Este proyecto extrae datos de órdenes desde una API local y los procesa con pandas.

## Instalación

Instalar dependencias con uv:

```bash
uv sync
```

## Uso

Ejecutar el script:

```bash
uv run python extraer_ordenes.py
```

Ejecutar los tests:

```bash
uv run pytest tests/ -v
```

El script:
- Consulta la API en http://localhost:8000/orders
- Procesa los datos con pandas
- Filtra solo las órdenes con estado 'delivered'
- Guarda los resultados en formato parquet

## Requisitos

- Python 3.9+
- API corriendo en localhost:8000
