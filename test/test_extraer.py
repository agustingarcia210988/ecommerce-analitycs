from extraer_ordenes import procesar_ordenes

def test_procesar_ordenes():
    # Datos de prueba
    datos_prueba = {
        'orders': [
            {
                'order_id': 'ORD-001',
                'customer_id': 'CUST-001',
                'order_date': '2024-11-15',
                'status': 'pending',
                'payment_method': 'credit_card',
                'shipping_address': 'Calle Test 123',
                'subtotal': 100.0,
                'discount_total': 10.0,
                'tax_total': 21.0,
                'shipping_cost': 5.0,
                'total_amount': 116.0,
                'items_count': 1
            }
        ]
    }
    
    # Proceso los datos
    df = procesar_ordenes(datos_prueba)
    
    # Verifico que funcione
    assert len(df) == 1
    assert df['id_orden'][0] == 'ORD-001'
    assert df['total'][0] == 116.0
    assert 'estado' in df.columns
    
    print("Test pasó correctamente!")

if __name__ == "__main__":
    test_procesar_ordenes()
