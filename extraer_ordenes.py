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

def main():
    # Fecha de prueba
    fecha = "2024-11-15"
    
    print(f"Obteniendo órdenes del {fecha}...")
    datos = obtener_ordenes(fecha)
    
    print(f"Total de órdenes: {datos['total_count']}")
    
    # Proceso los datos
    df_ordenes = procesar_ordenes(datos)
    
    # Filtro solo las órdenes finalizadas
    df_finalizadas = df_ordenes[df_ordenes['estado'] == 'delivered']
    
    print(f"\nÓrdenes finalizadas: {len(df_finalizadas)}")
    print("\nPrimeras órdenes finalizadas:")
    print(df_finalizadas.head())
    
    # Guardo en parquet
    nombre_archivo = f"ordenes_{fecha}.parquet"
    df_finalizadas.to_parquet(nombre_archivo, index=False)
    print(f"\nDatos guardados en {nombre_archivo}")

if __name__ == "__main__":
    main()
