{{ config(materialized='table') }}

WITH fact_ventas AS (
    SELECT * FROM {{ ref('gld_fact_ventas') }}
),

dim_fecha AS (
    SELECT * FROM {{ ref('slv_dim_fecha') }}
)

SELECT
    fv.fecha,
    df.anio,
    df.mes,
    df.mes_nombre,
    df.dia,
    df.dia_semana_nombre,
    df.tipo_dia,
    df.semana_anio,
    df.trimestre,
    
    COUNT(DISTINCT fv.id_orden) as cantidad_ordenes,
    COUNT(DISTINCT fv.id_cliente) as clientes_unicos,
    SUM(fv.cantidad) as unidades_vendidas,
    ROUND(SUM(fv.total_item), 2) as total_vendido,
    ROUND(AVG(fv.total_orden), 2) as ticket_promedio,
    ROUND(SUM(fv.monto_descuento), 2) as descuento_total,
    ROUND(AVG(fv.descuento_pct), 2) as descuento_promedio_pct,
    ROUND(SUM(fv.costo_envio), 2) as envio_total,
    
    CURRENT_TIMESTAMP as fecha_carga

FROM fact_ventas fv
LEFT JOIN dim_fecha df ON fv.fecha = df.fecha
GROUP BY 
    fv.fecha, df.anio, df.mes, df.mes_nombre, df.dia, 
    df.dia_semana_nombre, df.tipo_dia, df.semana_anio, df.trimestre
ORDER BY fv.fecha