{{ config(materialized='table') }}

SELECT * FROM read_parquet('/opt/airflow/data/ordenes_*.parquet')