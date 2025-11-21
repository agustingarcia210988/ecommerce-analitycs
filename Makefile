.PHONY: build up down restart logs test clean

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

restart:
	docker-compose down
	docker-compose up -d

logs:
	docker-compose logs -f airflow-scheduler

test:
	docker-compose exec airflow-scheduler airflow dags test etl_ordenes_diario 2025-11-15

backfill:
	docker-compose exec airflow-scheduler airflow dags backfill etl_ordenes_diario --start-date 2025-11-10 --end-date 2025-11-20 --reset-dagruns

clean:
	rm -rf logs/*
	rm -f ordenes_analytics/ordenes.duckdb
	rm -f ordenes_analytics/ordenes.duckdb.wal

pytest:
	uv run pytest tests/ -v