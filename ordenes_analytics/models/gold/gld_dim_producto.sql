{{ config(materialized='table') }}

WITH productos AS (
    SELECT DISTINCT
        codigo_producto,
        nombre_producto,
        categoria
    FROM {{ ref('slv_items') }}
)

SELECT
    {{ generate_surrogate_key(['codigo_producto']) }} as sk_producto,
    codigo_producto,
    nombre_producto,
    categoria,
    CURRENT_TIMESTAMP as fecha_carga
FROM productos