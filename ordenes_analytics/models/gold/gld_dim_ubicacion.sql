{{ config(materialized='table') }}

WITH ubicaciones AS (
    SELECT DISTINCT
        provincia,
        ciudad,
        codigo_postal
    FROM {{ ref('slv_ordenes') }}
)

SELECT
    {{ generate_surrogate_key(['provincia', 'ciudad', 'codigo_postal']) }} as sk_ubicacion,
    provincia,
    ciudad,
    codigo_postal,
    CASE provincia
        WHEN 'Buenos Aires' THEN 'Centro'
        WHEN 'CABA' THEN 'Centro'
        WHEN 'Cordoba' THEN 'Centro'
        WHEN 'Santa Fe' THEN 'Centro'
        WHEN 'Mendoza' THEN 'Cuyo'
        WHEN 'Tucuman' THEN 'Norte'
        WHEN 'Salta' THEN 'Norte'
        WHEN 'Neuquen' THEN 'Patagonia'
        ELSE 'Otro'
    END as region,
    CURRENT_TIMESTAMP as fecha_carga
FROM ubicaciones