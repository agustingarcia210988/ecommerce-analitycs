from extraer_ordenes import aplicar_transformaciones, calcular_metricas, filtrar_ordenes_entregadas
import pandas as pd
import pytest


def test_aplicar_transformaciones():
    """Test que verifica las transformaciones de datos"""
    df_prueba = pd.DataFrame({
        'id_orden': ['ORD-001', 'ORD-002'],
        'id_cliente': ['CUST-001', 'CUST-002'],
        'fecha': ['2025-11-15', '2025-11-16'],
        'timestamp_orden': ['2025-11-15T10:00:00', '2025-11-16T14:30:00'],
        'estado': ['delivered', 'pending'],
        'metodo_pago': ['credit_card', 'mercadopago'],
        'calle': ['Av. Corrientes 1234', 'Calle San Martin 567'],
        'ciudad': ['Palermo', 'Rosario'],
        'provincia': ['CABA', 'Santa Fe'],
        'codigo_postal': ['1425', '2000'],
        'direccion_completa': ['Calle 1', None],
        'subtotal': [100.0, 200.0],
        'descuento_total': [10.0, 40.0],
        'impuestos': [18.9, 33.6],
        'costo_envio': [50.0, 100.0],
        'total': [158.9, 293.6],
        'cantidad_items': [1, 2]
    })
    
    df_resultado = aplicar_transformaciones(df_prueba)
    
    assert df_resultado['porcentaje_descuento'].iloc[0] == 10.0
    assert df_resultado['porcentaje_descuento'].iloc[1] == 20.0
    assert df_resultado['direccion_completa'].iloc[1] == 'Sin direccion'
    assert pd.api.types.is_datetime64_any_dtype(df_resultado['fecha'])
    assert df_resultado['precio_promedio_item'].iloc[0] == 158.9
    assert df_resultado['precio_promedio_item'].iloc[1] == 146.8


def test_filtrar_ordenes_entregadas():
    """Test que verifica el filtrado de ordenes"""
    df_prueba = pd.DataFrame({
        'id_orden': ['ORD-001', 'ORD-002', 'ORD-003', 'ORD-004'],
        'estado': ['delivered', 'pending', 'delivered', 'cancelled'],
        'total': [100.0, 200.0, 150.0, 50.0]
    })
    
    df_resultado = filtrar_ordenes_entregadas(df_prueba)
    
    assert len(df_resultado) == 2
    assert all(df_resultado['estado'] == 'delivered')
    assert list(df_resultado['id_orden']) == ['ORD-001', 'ORD-003']


def test_calcular_metricas():
    """Test que verifica calculo de metricas"""
    df_prueba = pd.DataFrame({
        'total': [100.0, 200.0, 150.0],
        'cantidad_items': [1, 2, 1],
        'descuento_total': [10.0, 20.0, 15.0]
    })
    
    metricas = calcular_metricas(df_prueba)
    
    assert metricas['total_vendido'] == 450.0
    assert metricas['ticket_promedio'] == 150.0
    assert metricas['total_items_vendidos'] == 4
    assert metricas['descuento_total'] == 45.0
    assert metricas['cantidad_ordenes'] == 3


def test_calcular_metricas_dataframe_vacio():
    """Test que verifica el comportamiento con DataFrame vacio"""
    df_vacio = pd.DataFrame({
        'total': [],
        'cantidad_items': [],
        'descuento_total': []
    })
    
    metricas = calcular_metricas(df_vacio)
    
    assert metricas['total_vendido'] == 0.0
    assert metricas['cantidad_ordenes'] == 0


if __name__ == "__main__":
    test_aplicar_transformaciones()
    test_filtrar_ordenes_entregadas()
    test_calcular_metricas()
    test_calcular_metricas_dataframe_vacio()
    print("Todos los tests pasaron!")