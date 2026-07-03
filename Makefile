# --- Environment / dependencies ---
install:  ## Install dependencies with Poetry
	poetry install

pre-commit.install:  ## Install git hooks
	poetry run pre-commit install

# --- Dependencies in Docker (Postgres + Redis) ---
compose.deps.dev:  ## Start Postgres + Redis
	docker compose -f compose.deps.dev.yml up -d

compose.deps.dev.down:  ## Stop Postgres + Redis
	docker compose -f compose.deps.dev.yml down

# --- Full stack in Docker (backend + celery + deps) ---
up:  ## Start the backend and celery (uses compose.deps.dev for db/redis)
	docker compose -f compose.deps.dev.yml -f compose.dev.yml up -d --build

down:  ## Stop the full stack
	docker compose -f compose.deps.dev.yml -f compose.dev.yml down

logs:  ## Follow backend logs
	docker compose -f compose.dev.yml logs -f backend

# --- Django management (local through Poetry) ---
makemigrations:  ## Create migrations
	poetry run python src/manage.py makemigrations

migrate:  ## Apply migrations
	poetry run python src/manage.py migrate

createsuperuser:  ## Create an admin user
	poetry run python src/manage.py createsuperuser

run:  ## Run the development server (http://localhost:8000)
	poetry run python src/manage.py runserver

celery:  ## Run a celery worker locally
	cd src && poetry run celery -A django_project.celery.app worker -l INFO -Q celery

# --- Code quality ---
lint:  ## Format, lint, and type-check
	poetry run ruff format src/
	poetry run ruff check src/ --fix
	poetry run mypy src/

test:  ## Run tests
	poetry run pytest src/
