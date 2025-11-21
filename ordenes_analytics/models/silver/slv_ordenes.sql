{{ config(materialized='table') }}

WITH ordenes_raw AS (
    SELECT * FROM {{ ref('brz_ordenes') }}
)

SELECT
    {{ generate_surrogate_key(['id_orden']) }} as sk_orden,
    
    id_orden,
    id_cliente,
    
    CAST(fecha AS DATE) as fecha,
    CAST(timestamp_orden AS TIMESTAMP) as timestamp_orden,
    
    estado,
    metodo_pago,
    
    calle,
    ciudad,
    provincia,
    codigo_postal,
    direccion_completa,
    
    ROUND(subtotal, 2) as subtotal,
    ROUND(descuento_total, 2) as descuento_total,
    ROUND(impuestos, 2) as impuestos,
    ROUND(costo_envio, 2) as costo_envio,
    ROUND(total, 2) as total,
    cantidad_items,
    ROUND(porcentaje_descuento, 2) as porcentaje_descuento,
    ROUND(precio_promedio_item, 2) as precio_promedio_item,
    
    CURRENT_TIMESTAMP as fecha_carga
    
FROM ordenes_raw