{{ config(materialized='table') }}

WITH items_raw AS (
    SELECT * FROM {{ ref('brz_items') }}
)

SELECT
    {{ generate_surrogate_key(['id_orden', 'id_item']) }} as sk_item,
    {{ generate_surrogate_key(['id_orden']) }} as sk_orden,
    
    id_orden,
    id_item,
    codigo_producto,
    
    nombre_producto,
    categoria,
    
    cantidad,
    ROUND(precio_unitario, 2) as precio_unitario,
    ROUND(porcentaje_descuento, 2) as porcentaje_descuento,
    ROUND(monto_descuento, 2) as monto_descuento,
    ROUND(subtotal, 2) as subtotal,
    ROUND(impuesto, 2) as impuesto,
    ROUND(total, 2) as total,
    
    CURRENT_TIMESTAMP as fecha_carga
    
FROM items_raw