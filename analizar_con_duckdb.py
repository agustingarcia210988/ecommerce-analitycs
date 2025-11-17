import duckdb

# Conectar a DuckDB (en memoria)
con = duckdb.connect()

# Leer el parquet directamente
df = con.execute("""
    SELECT * 
    FROM 'data/ordenes_2024-11-15.parquet'
""").df()

print(df.head())

con.close()