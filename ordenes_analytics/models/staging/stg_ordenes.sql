WITH raw_ordenes AS (
    SELECT * FROM read_parquet('../data/ordenes_*.parquet')
)

SELECT
    id_orden,
    id_cliente,
    fecha,
    estado,
    metodo_pago,
    COALESCE(direccion, 'Sin dirección') as direccion_entrega,
    subtotal,
    descuento,
    impuestos,
    envio,
    total,
    cantidad_items,
    porcentaje_descuento,
    precio_promedio_item,
    CURRENT_TIMESTAMP as fecha_carga
FROM raw_ordenes
WHERE estado = 'delivered'