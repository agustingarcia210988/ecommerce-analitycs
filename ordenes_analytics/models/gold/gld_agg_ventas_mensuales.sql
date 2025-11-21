{{ config(materialized='table') }}

WITH ventas_diarias AS (
    SELECT * FROM {{ ref('gld_agg_ventas_diarias') }}
)

SELECT
    anio,
    mes,
    mes_nombre,
    trimestre,
    
    SUM(cantidad_ordenes) as cantidad_ordenes,
    SUM(clientes_unicos) as clientes_totales,
    SUM(unidades_vendidas) as unidades_vendidas,
    ROUND(SUM(total_vendido), 2) as total_vendido,
    ROUND(AVG(ticket_promedio), 2) as ticket_promedio,
    ROUND(SUM(descuento_total), 2) as descuento_total,
    ROUND(AVG(descuento_promedio_pct), 2) as descuento_promedio_pct,
    
    COUNT(DISTINCT fecha) as dias_con_ventas,
    ROUND(SUM(total_vendido) / COUNT(DISTINCT fecha), 2) as promedio_diario,
    
    CURRENT_TIMESTAMP as fecha_carga

FROM ventas_diarias
GROUP BY anio, mes, mes_nombre, trimestre
ORDER BY anio, mes