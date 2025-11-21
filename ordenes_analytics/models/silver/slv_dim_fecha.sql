{{ config(materialized='table') }}

WITH fechas_ordenes AS (
    SELECT DISTINCT CAST(fecha AS DATE) as fecha
    FROM {{ ref('brz_ordenes') }}
)

SELECT
    {{ generate_surrogate_key(['fecha']) }} as sk_fecha,
    {{ extract_date_parts('fecha') }}
FROM fechas_ordenes