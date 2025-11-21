# extraer_ordenes.py
import pandas as pd
import requests
import os
from typing import Dict, List

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000')

def extraer_desde_api(fecha: str, url_base: str = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Extrae órdenes y detalle de items de la API"""
    if url_base is None:
        url_base = API_BASE_URL
    
    url = f"{url_base}/orders?fecha={fecha}&limit=20"
    
    respuesta = requests.get(url, timeout=30)
    respuesta.raise_for_status()
    datos = respuesta.json()
    
    ordenes = datos['orders']
    
    # DataFrame de cabecera de órdenes
    lista_ordenes = []
    # DataFrame de detalle de items
    lista_items = []
    
    for orden in ordenes:
        # Cabecera
        lista_ordenes.append({
            'id_orden': orden['order_id'],
            'id_cliente': orden['customer_id'],
            'fecha': orden['order_date'],
            'timestamp_orden': orden['order_timestamp'],
            'estado': orden['status'],
            'metodo_pago': orden['payment_method'],
            'calle': orden['shipping_street'],
            'ciudad': orden['shipping_city'],
            'provincia': orden['shipping_province'],
            'codigo_postal': orden['shipping_postal_code'],
            'direccion_completa': orden['shipping_address'],
            'subtotal': orden['subtotal'],
            'descuento_total': orden['discount_total'],
            'impuestos': orden['tax_total'],
            'costo_envio': orden['shipping_cost'],
            'total': orden['total_amount'],
            'cantidad_items': orden['items_count']
        })
        
        # Detalle de items
        for item in orden['items']:
            lista_items.append({
                'id_orden': orden['order_id'],
                'id_item': item['item_id'],
                'codigo_producto': item['product_code'],
                'nombre_producto': item['product_name'],
                'categoria': item['category'],
                'cantidad': item['quantity'],
                'precio_unitario': item['unit_price'],
                'porcentaje_descuento': item['discount_percentage'],
                'monto_descuento': item['discount_amount'],
                'subtotal': item['subtotal'],
                'impuesto': item['tax_amount'],
                'total': item['total']
            })
    
    df_ordenes = pd.DataFrame(lista_ordenes)
    df_items = pd.DataFrame(lista_items)
    
    return df_ordenes, df_items

def aplicar_transformaciones(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica transformaciones al DataFrame de órdenes"""
    df = df.copy()
    df['fecha'] = pd.to_datetime(df['fecha'])
    df['porcentaje_descuento'] = (df['descuento_total'] / df['subtotal'] * 100).round(2)
    df['precio_promedio_item'] = (df['total'] / df['cantidad_items']).round(2)
    df['direccion_completa'] = df['direccion_completa'].fillna('Sin dirección')
    return df

def filtrar_ordenes_entregadas(df: pd.DataFrame) -> pd.DataFrame:
    """Filtra solo las órdenes con status 'delivered'"""
    return df[df['estado'] == 'delivered'].copy()

def calcular_metricas(df: pd.DataFrame) -> Dict:
    """Calcula métricas agregadas de las órdenes"""
    return {
        'total_vendido': df['total'].sum(),
        'ticket_promedio': df['total'].mean(),
        'total_items_vendidos': df['cantidad_items'].sum(),
        'descuento_total': df['descuento_total'].sum(),
        'cantidad_ordenes': len(df)
    }

def procesar_ordenes(fecha: str, url_base: str = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Pipeline completo: extrae, transforma y filtra"""
    df_ordenes, df_items = extraer_desde_api(fecha, url_base)
    df_ordenes = aplicar_transformaciones(df_ordenes)
    df_ordenes_entregadas = filtrar_ordenes_entregadas(df_ordenes)
    
    # Filtrar items solo de órdenes entregadas
    ids_entregadas = df_ordenes_entregadas['id_orden'].tolist()
    df_items_entregadas = df_items[df_items['id_orden'].isin(ids_entregadas)].copy()
    
    return df_ordenes_entregadas, df_items_entregadas

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--fecha', default='2025-11-15')
    args = parser.parse_args()
    
    print(f"API URL: {API_BASE_URL}")
    
    df_ordenes, df_items = procesar_ordenes(args.fecha)
    
    print(f"Órdenes procesadas: {len(df_ordenes)}")
    print(f"Items procesados: {len(df_items)}")
    
    # Guardar ambos archivos
    df_ordenes.to_parquet(f"data/ordenes_{args.fecha}.parquet", index=False)
    df_items.to_parquet(f"data/items_{args.fecha}.parquet", index=False)
    
    print(f" Guardado en: data/ordenes_{args.fecha}.parquet")
    print(f" Guardado en: data/items_{args.fecha}.parquet")
