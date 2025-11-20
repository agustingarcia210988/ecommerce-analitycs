from extraer_ordenes import procesar_ordenes, aplicar_transformaciones, calcular_metricas
import pandas as pd


def test_aplicar_transformaciones():
    # DataFrame de prueba
    df_prueba = pd.DataFrame({
        'id_orden': ['ORD-001', 'ORD-002'],
        'fecha': ['2024-11-15', '2024-11-16'],
        'subtotal': [100.0, 200.0],
        'descuento': [10.0, 40.0],
        'total': [116.0, 232.0],
        'cantidad_items': [1, 2],
        'direccion': ['Calle 1', None]
    })
    
    # Aplico transformaciones
    df_resultado = aplicar_transformaciones(df_prueba)
    
    # Verifico porcentaje de descuento
    assert df_resultado['porcentaje_descuento'][0] == 10.0
    assert df_resultado['porcentaje_descuento'][1] == 20.0
    
    
    # Verifico que rellenó direcciones vacías
    assert df_resultado['direccion'][1] == 'Sin dirección'
    
    # Verifico que fecha es datetime
    assert pd.api.types.is_datetime64_any_dtype(df_resultado['fecha'])
    
    print("Test aplicar_transformaciones pasó")

def test_calcular_metricas():
    # DataFrame de prueba
    df_prueba = pd.DataFrame({
        'total': [100.0, 200.0, 150.0],
        'cantidad_items': [1, 2, 1],
        'descuento': [10.0, 20.0, 15.0]
    })
    
    metricas = calcular_metricas(df_prueba)
    
    # Verifico métricas
    assert metricas['total_vendido'] == 450.0
    assert metricas['ticket_promedio'] == 150.0
    assert metricas['total_items_vendidos'] == 4
    assert metricas['descuento_total'] == 45.0
    assert metricas['cantidad_ordenes'] == 3
    
    print(" Test calcular_metricas pasó")

    

if __name__ == "__main__":
    test_aplicar_transformaciones()
    test_calcular_metricas()
    print("\n✅ Todos los tests pasaron!")