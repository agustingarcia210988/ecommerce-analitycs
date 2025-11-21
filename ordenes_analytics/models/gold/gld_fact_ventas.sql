{{ config(materialized='table') }}

WITH ordenes AS (
    SELECT * FROM {{ ref('slv_ordenes') }}
),

items AS (
    SELECT * FROM {{ ref('slv_items') }}
),

dim_fecha AS (
    SELECT * FROM {{ ref('slv_dim_fecha') }}
)

SELECT
    i.sk_item as sk_venta,
    o.sk_orden,
    {{ generate_surrogate_key(['o.id_cliente']) }} as sk_cliente,
    {{ generate_surrogate_key(['i.codigo_producto']) }} as sk_producto,
    {{ generate_surrogate_key(['o.provincia', 'o.ciudad', 'o.codigo_postal']) }} as sk_ubicacion,
    df.sk_fecha,
    
    o.id_orden,
    i.id_item,
    o.id_cliente,
    i.codigo_producto,
    
    o.fecha,
    o.timestamp_orden,
    
    o.estado,
    o.metodo_pago,
    i.categoria,
    o.provincia,
    o.ciudad,
    
    i.cantidad,
    i.precio_unitario,
    i.porcentaje_descuento as descuento_pct,
    i.monto_descuento,
    i.subtotal,
    i.impuesto,
    i.total as total_item,
    
    o.total as total_orden,
    o.costo_envio,
    
    CURRENT_TIMESTAMP as fecha_carga

FROM items i
INNER JOIN ordenes o ON i.id_orden = o.id_orden
LEFT JOIN dim_fecha df ON o.fecha = df.fecha