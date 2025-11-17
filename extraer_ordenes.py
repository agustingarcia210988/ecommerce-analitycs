import requests
import pandas as pd
from datetime import datetime

# URL de la API
URL_BASE = "http://localhost:8000"

def obtener_ordenes(fecha):
    """Trae las órdenes de una fecha"""
    url = f"{URL_BASE}/orders?fecha={fecha}"
    respuesta = requests.get(url)
    return respuesta.json()

def procesar_ordenes(datos):
    """Convierte los datos a un DataFrame de pandas"""
    ordenes = datos['orders']
    
    # Armo una lista con los datos que me interesan
    lista_ordenes = []
    for orden in ordenes:
        lista_ordenes.append({
            'id_orden': orden['order_id'],
            'id_cliente': orden['customer_id'],
            'fecha': orden['order_date'],
            'estado': orden['status'],
            'metodo_pago': orden['payment_method'],
            'direccion': orden['shipping_address'],
            'subtotal': orden['subtotal'],
            'descuento': orden['discount_total'],
            'impuestos': orden['tax_total'],
            'envio': orden['shipping_cost'],
            'total': orden['total_amount'],
            'cantidad_items': orden['items_count']
        })
    
    df = pd.DataFrame(lista_ordenes)
    return df

def aplicar_transformaciones(df):
    """Aplica transformaciones al DataFrame de órdenes"""
    
    # Convertir fecha a datetime
    df['fecha'] = pd.to_datetime(df['fecha'])
    
    # Calcular porcentaje de descuento
    df['porcentaje_descuento'] = (df['descuento'] / df['subtotal'] * 100).round(2)
    
    # Precio promedio por item
    df['precio_promedio_item'] = (df['total'] / df['cantidad_items']).round(2)
    
    
    # Rellenar direcciones vacías
    df['direccion'] = df['direccion'].fillna('Sin dirección')
    
    return df

def calcular_metricas(df):
    """Calcula métricas agregadas del DataFrame"""
    metricas = {
        'total_vendido': df['total'].sum(),
        'ticket_promedio': df['total'].mean(),
        'total_items_vendidos': df['cantidad_items'].sum(),
        'descuento_total': df['descuento'].sum(),
        'cantidad_ordenes': len(df)
    }
    return metricas

def main():
    # Fecha de prueba
    fecha = "2024-11-15"
    
    print(f"Obteniendo órdenes del {fecha}...")
    datos = obtener_ordenes(fecha)
    
    print(f"Total de órdenes: {datos['total_count']}")
    
    # Proceso los datos
    df_ordenes = procesar_ordenes(datos)
    
    # Aplico transformaciones
    df_ordenes = aplicar_transformaciones(df_ordenes)
    
    # Filtro solo las órdenes finalizadas
    df_finalizadas = df_ordenes[df_ordenes['estado'] == 'delivered']
    
    print(f"\nÓrdenes finalizadas: {len(df_finalizadas)}")
    
    # Calculo métricas
    metricas = calcular_metricas(df_finalizadas)
    print("\nMétricas:")
    for key, value in metricas.items():
        print(f"  {key}: {value}")
    
    # Guardo en parquet dentro de carpeta data
    nombre_archivo = f"data/ordenes_{fecha}.parquet"
    df_finalizadas.to_parquet(nombre_archivo, index=False)
    print(f"\nDatos guardados en {nombre_archivo}")

if __name__ == "__main__":
    main()