# extraer_ordenes.py
import pandas as pd
import requests
import os
from typing import Dict, List
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Obtener URL de la API desde environment
API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000')

def extraer_desde_api(fecha: str, url_base: str = None) -> pd.DataFrame:
    """Extrae órdenes de la API para una fecha específica"""
    # Si no se pasa url_base, usar la del environment
    if url_base is None:
        url_base = API_BASE_URL
    
    url = f"{url_base}/orders?fecha={fecha}"
    
    respuesta = requests.get(url, timeout=30)
    respuesta.raise_for_status()
    datos = respuesta.json()
    
    ordenes = datos['orders']
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
    
    return pd.DataFrame(lista_ordenes)

def aplicar_transformaciones(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica transformaciones al DataFrame"""
    df = df.copy()
    
    # Convertir fecha a datetime
    df['fecha'] = pd.to_datetime(df['fecha'])
    
    # Calcular porcentaje de descuento
    df['porcentaje_descuento'] = (df['descuento'] / df['subtotal'] * 100).round(2)
    
    # Precio promedio por item
    df['precio_promedio_item'] = (df['total'] / df['cantidad_items']).round(2)
    
    # Rellenar direcciones vacías
    df['direccion'] = df['direccion'].fillna('Sin dirección')
    
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
        'descuento_total': df['descuento'].sum(),
        'cantidad_ordenes': len(df)
    }

def procesar_ordenes(fecha: str, url_base: str = None) -> pd.DataFrame:
    """Pipeline completo: extrae, transforma y filtra"""
    df = extraer_desde_api(fecha, url_base)
    df = aplicar_transformaciones(df)
    df = filtrar_ordenes_entregadas(df)
    return df

# Script standalone (si lo ejecutás directamente)
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--fecha', default='2024-11-15')
    parser.add_argument('--url', default=None, help='URL base de la API')
    args = parser.parse_args()
    
    print(f"🌐 API URL: {args.url or API_BASE_URL}")
    
    df_resultado = procesar_ordenes(args.fecha, args.url)
    
    print(f"✅ Órdenes procesadas: {len(df_resultado)}")
    print("\nMétricas:")
    for k, v in calcular_metricas(df_resultado).items():
        print(f"  {k}: {v}")
    
    # Guardar
    archivo = f"data/ordenes_{args.fecha}.parquet"
    df_resultado.to_parquet(archivo, index=False)
    print(f"\n💾 Guardado en: {archivo}")