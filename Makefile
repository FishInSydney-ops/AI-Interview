.PHONY: install configure migrate api portal admin init-admin check

install:
	uv sync --project backend --locked
	npm ci

configure:
	cd backend && uv run python -m app.entry.cli configure

init-admin:
	cd backend && uv run python -m app.entry.cli create-admin

migrate:
	cd backend && uv run alembic upgrade head

api:
	cd backend && uv run uvicorn app.entry.main:create_app --factory --host 127.0.0.1 --port 8000 --reload --no-proxy-headers

portal:
	npm run dev:portal

admin:
	npm run dev:admin

check:
	cd backend && uv run ruff check --config pyproject.toml app migrations tests ../scripts/export_schema.py
	cd backend && uv run ruff format --config pyproject.toml --check app migrations tests ../scripts/export_schema.py
	cd backend && uv run pytest -q
	npm run build
