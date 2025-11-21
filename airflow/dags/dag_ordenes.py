from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
import subprocess

sys.path.insert(0, '/opt/airflow/project')


def extraer_ordenes_fecha(**context):
    """Task de Airflow que extrae ordenes y items"""
    from extraer_ordenes import procesar_ordenes
    
    fecha_ejecucion = context['ds']
    api_url = 'http://host.docker.internal:8000'
    
    print(f"Extrayendo ordenes para: {fecha_ejecucion}")
    print(f"API URL: {api_url}")
    
    df_ordenes, df_items = procesar_ordenes(fecha_ejecucion, api_url)
    
    print(f"Ordenes extraidas: {len(df_ordenes)}")
    print(f"Items extraidos: {len(df_items)}")
    
    archivo_ordenes = f"/opt/airflow/data/ordenes_{fecha_ejecucion}.parquet"
    archivo_items = f"/opt/airflow/data/items_{fecha_ejecucion}.parquet"
    
    df_ordenes.to_parquet(archivo_ordenes, index=False)
    df_items.to_parquet(archivo_items, index=False)
    
    print(f"Guardado: {archivo_ordenes}")
    print(f"Guardado: {archivo_items}")
    
    return {'ordenes': len(df_ordenes), 'items': len(df_items)}


def ejecutar_dbt(**context):
    """Ejecuta los modelos de dbt (Bronze, Silver, Gold)"""
    
    fecha_ejecucion = context['ds']
    print(f"Ejecutando transformaciones dbt para fecha: {fecha_ejecucion}")
    
    dbt_dir = "/opt/airflow/project/ordenes_analytics"
    
    resultado = subprocess.run(
        ["dbt", "run", "--profiles-dir", dbt_dir],
        cwd=dbt_dir,
        capture_output=True,
        text=True
    )
    
    print(resultado.stdout)
    
    if resultado.returncode != 0:
        print("Error en dbt:")
        print(resultado.stderr)
        raise Exception(f"dbt fallo con codigo {resultado.returncode}")
    
    print("Modelos dbt ejecutados exitosamente")
    print("Capas procesadas: Bronze -> Silver -> Gold")


def ejecutar_dbt_tests(**context):
    """Ejecuta los tests de dbt"""
    
    print("Ejecutando tests de dbt...")
    
    dbt_dir = "/opt/airflow/project/ordenes_analytics"
    
    resultado = subprocess.run(
        ["dbt", "test", "--profiles-dir", dbt_dir],
        cwd=dbt_dir,
        capture_output=True,
        text=True
    )
    
    print(resultado.stdout)
    
    if resultado.returncode != 0:
        print("Algunos tests fallaron:")
        print(resultado.stderr)
    else:
        print("Todos los tests de dbt pasaron")


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'etl_ordenes_diario',
    default_args=default_args,
    description='ETL diario de ordenes con arquitectura Medallion (Bronze/Silver/Gold)',
    schedule_interval='0 2 * * *',
    start_date=datetime(2025, 11, 1),
    catchup=True,
    max_active_runs=1,
    tags=['ordenes', 'etl', 'dbt', 'medallion'],
) as dag:
    
    task_extraer = PythonOperator(
        task_id='extraer_ordenes',
        python_callable=extraer_ordenes_fecha,
        provide_context=True,
    )
    
    task_dbt = PythonOperator(
        task_id='ejecutar_dbt',
        python_callable=ejecutar_dbt,
        provide_context=True,
    )
    
    task_dbt_tests = PythonOperator(
        task_id='ejecutar_dbt_tests',
        python_callable=ejecutar_dbt_tests,
        provide_context=True,
    )
    
    task_extraer >> task_dbt >> task_dbt_tests