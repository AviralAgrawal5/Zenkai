.PHONY: dev test lint format build down logs seed demo

# ── Development ───────────────────────────────────────────────────────────────
dev:
	docker compose -f docker-compose.yml -f docker-compose.override.yml up --build

down:
	docker compose -f docker-compose.yml -f docker-compose.override.yml down -v

logs:
	docker compose logs -f

build:
	docker compose -f docker-compose.yml -f docker-compose.override.yml build

# ── Code quality ──────────────────────────────────────────────────────────────
lint:
	ruff check services/ scripts/
	black --check services/ scripts/

format:
	black services/ scripts/
	ruff check --fix services/ scripts/

# ── Tests ─────────────────────────────────────────────────────────────────────
test:
	pytest services/ -v --asyncio-mode=auto

# ── Data & demo ───────────────────────────────────────────────────────────────
seed:
	python scripts/seed.py

demo:
	python scripts/demo_happy_path.py
