{{ config(materialized='table') }}

WITH clientes AS (
    SELECT DISTINCT
        id_cliente,
        provincia,
        ciudad
    FROM {{ ref('slv_ordenes') }}
)

SELECT
    {{ generate_surrogate_key(['id_cliente']) }} as sk_cliente,
    id_cliente,
    provincia as provincia_principal,
    ciudad as ciudad_principal,
    CURRENT_TIMESTAMP as fecha_carga
FROM clientes