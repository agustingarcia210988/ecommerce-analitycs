{{ config(materialized='table') }}

SELECT * FROM read_parquet('/opt/airflow/data/items_*.parquet')