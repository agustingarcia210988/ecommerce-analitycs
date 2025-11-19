{{ config(materialized='table') }}

WITH ordenes_staging AS (
    SELECT * FROM {{ ref('stg_ordenes') }}
)

SELECT
    COUNT(*) as cantidad_ordenes,
    SUM(total) as total_vendido,
    ROUND(AVG(total), 2) as ticket_promedio,
    SUM(cantidad_items) as items_vendidos,
    ROUND(SUM(descuento), 2) as descuento_total,
    ROUND(AVG(porcentaje_descuento), 2) as descuento_promedio_pct
FROM ordenes_staging
GROUP BY fecha
ORDER BY total_vendido DESC