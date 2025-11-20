FROM apache/airflow:2.8.1-python3.11

# Copiar requirements
COPY requirements.txt /requirements.txt

# Instalar dependencias
RUN pip install --no-cache-dir -r /requirements.txt
