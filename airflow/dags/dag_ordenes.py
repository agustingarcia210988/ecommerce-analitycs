# airflow/dags/dag_ordenes.py
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
import os

# Agregar el path del proyecto
sys.path.insert(0, '/opt/airflow/project')

# Importar las funciones
from extraer_ordenes import procesar_ordenes

def extraer_ordenes_fecha(**context):
    """Task de Airflow que usa las funciones del módulo"""
    fecha_ejecucion = context['ds']
    
    # Obtener URL de la API desde variables de entorno de Airflow
    # En Docker, la API está en host.docker.internal
    api_url = os.getenv('API_BASE_URL', 'http://host.docker.internal:8000')
    
    print(f"📅 Extrayendo órdenes para: {fecha_ejecucion}")
    print(f"🌐 API URL: {api_url}")
    
    # Usar la función importada
    df_finalizadas = procesar_ordenes(
        fecha=fecha_ejecucion,
        url_base=api_url
    )
    
    print(f"📊 Órdenes finalizadas: {len(df_finalizadas)}")
    
    # Guardar
    archivo_salida = f"/opt/airflow/data/ordenes_{fecha_ejecucion}.parquet"
    df_finalizadas.to_parquet(archivo_salida, index=False)
    
    print(f"💾 Datos guardados en: {archivo_salida}")
    
    return archivo_salida

def ejecutar_dbt(**context):
    """Ejecuta los modelos de dbt"""
    import subprocess
    
    fecha_ejecucion = context['ds']
    print(f"🔄 Ejecutando transformaciones dbt para fecha: {fecha_ejecucion}")
    
    dbt_dir = "/opt/airflow/project/ordenes_analytics"
    
    resultado = subprocess.run(
        ["dbt", "run", "--profiles-dir", dbt_dir],
        cwd=dbt_dir,
        capture_output=True,
        text=True
    )
    
    print(resultado.stdout)
    
    if resultado.returncode != 0:
        print("❌ Error en dbt:")
        print(resultado.stderr)
        raise Exception(f"dbt falló con código {resultado.returncode}")
    
    print("✅ Modelos dbt ejecutados exitosamente")

# Argumentos por defecto del DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Definir el DAG
with DAG(
    'etl_ordenes_diario',
    default_args=default_args,
    description='ETL diario de órdenes con dbt',
    schedule_interval='0 2 * * *',
    start_date=datetime(2024, 11, 1),
    catchup=True,
    max_active_runs=1,
    tags=['ordenes', 'etl', 'dbt'],
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
    
    task_extraer >> task_dbt