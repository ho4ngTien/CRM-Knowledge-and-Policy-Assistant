.PHONY: help up down dev-db lint test migrate

help:
	@echo "Targets: up | down | dev-db | lint | test | migrate"

up:
	docker compose up -d

down:
	docker compose down

dev-db:
	docker compose up -d db redis

lint:
	cd backend && ruff check . && mypy src
	cd frontend && npm run lint

test:
	cd backend && pytest -q
	cd frontend && npm run build

migrate:
	cd backend && alembic upgrade head
