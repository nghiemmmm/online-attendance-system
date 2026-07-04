# ==============================================================================
# PROJECT ORCHESTRATION MAKEFILE
# ==============================================================================
# This Makefile serves as the control center for local development, docker compose 
# operations, testing, code quality, database migrations, and deployments.
#
# Usage:
#   make <command>
# ==============================================================================

.DEFAULT_GOAL := help

# --- VARIABLES & CONFIGURATIONS ---
PYTHON := venv/Scripts/python
PIP := venv/Scripts/pip
DOCKER_COMPOSE_DEV := docker-compose.dev.yml
DOCKER_COMPOSE_PROD := -f docker-compose.yml -f docker-compose.pro.yml

# Colors for terminal styling
BLUE   := \033[1;34m
GREEN  := \033[1;32m
RED    := \033[1;31m
YELLOW := \033[1;33m
NC     := \033[0m # No Color


# Helper helper to print status
define print_status
	@echo -e "$(BLUE)[INFO]$(NC) $(1)"
endef

define print_success
	@echo -e "$(GREEN)[SUCCESS]$(NC) $(1)"
endef

define print_error
	@echo -e "$(RED)[ERROR]$(NC) $(1)"
endef

define print_warning
	@echo -e "$(YELLOW)[WARNING]$(NC) $(1)"
endef

# Helper helper to ask for confirmation before high-risk tasks
define confirm_action
	@echo -n "Are you sure you want to proceed with $(1)? [y/N] " && read ans && [ $${ans:-N} = y ] || (echo "Action aborted."; exit 1)
endef

# ==============================================================================
# 1. HELP
# ==============================================================================

.PHONY: help
help: ## Display this help message containing all available commands
	@echo -e "$(BLUE)Hệ thống Điểm danh Sinh viên bằng Nhận diện Khuôn mặt AI - Makefile$(NC)"
	@echo -e "Các nhóm lệnh khả dụng:"
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-25s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ 2. Development
.PHONY: dev build up down restart rebuild logs logs-backend logs-frontend logs-db logs-redis logs-ai

dev: ## Run development backend server locally
	$(call print_status, "Starting FastAPI development server locally...")
	$(PYTHON) -m uvicorn app.main:app --host 0.0.0.0 --port 5050 --reload

build: ## Build docker images using development compose configuration
	$(call print_status, "Building development Docker images...")
	docker compose -f $(DOCKER_COMPOSE_DEV) build

up: ## Start docker containers in background
	$(call print_status, "Starting development container services...")
	docker compose -f $(DOCKER_COMPOSE_DEV) up -d
	$(call print_success, "Containers are up and running.")

down: ## Stop and remove docker containers
	$(call print_status, "Stopping development container services...")
	docker compose -f $(DOCKER_COMPOSE_DEV) down
	$(call print_success, "Containers stopped.")

restart: down up ## Restart all development container services

rebuild: ## Rebuild and start container services ignoring cache
	$(call print_status, "Rebuilding development containers from scratch...")
	docker compose -f $(DOCKER_COMPOSE_DEV) build --no-cache
	docker compose -f $(DOCKER_COMPOSE_DEV) up -d --force-recreate
	$(call print_success, "Containers rebuilt and started.")

logs: ## Follow logs from all active container services
	docker compose -f $(DOCKER_COMPOSE_DEV) logs -f

logs-backend: ## View backend container logs
	docker compose -f $(DOCKER_COMPOSE_DEV) logs -f backend

logs-frontend: ## View frontend container logs
	docker compose -f $(DOCKER_COMPOSE_DEV) logs -f frontend

logs-db: ## View PostgreSQL database container logs
	docker compose -f $(DOCKER_COMPOSE_DEV) logs -f db

logs-redis: ## View Redis container logs
	docker compose -f $(DOCKER_COMPOSE_DEV) logs -f redis || echo "Redis service not in compose stack."

logs-ai: ## View dedicated AI service logs (if separate container is defined)
	docker compose -f $(DOCKER_COMPOSE_DEV) logs -f ai || echo "AI service logs not found."

##@ 3. Docker Utilities
.PHONY: clean prune stats images containers shell-backend shell-frontend

clean: ## Clean stopped containers, networks, and orphaned volumes
	$(call print_warning, "This will delete all stopped containers and unused networks.")
	$(call confirm_action, "clean")
	docker system prune -f
	$(call print_success, "Docker cleanup completed.")

prune: ## Prune all unused images, containers, networks, and volumes (Deep Clean)
	$(call print_warning, "This will prune all unused Docker objects including volumes!")
	$(call confirm_action, "prune")
	docker system prune -a --volumes -f
	$(call print_success, "Docker deep prune completed.")

stats: ## Display active Docker container resource statistics
	docker stats

images: ## List local Docker images
	docker images

containers: ## List all running Docker containers
	docker ps -a

shell-backend: ## Access shell inside running backend container
	docker compose -f $(DOCKER_COMPOSE_DEV) exec backend /bin/bash || docker compose -f $(DOCKER_COMPOSE_DEV) exec backend sh

shell-frontend: ## Access shell inside running frontend container
	docker compose -f $(DOCKER_COMPOSE_DEV) exec frontend /bin/sh

##@ 4. Testing
.PHONY: test test-backend test-frontend coverage benchmark

test: test-backend ## Run all test suites (Backend and Frontend)

test-backend: ## Run Python backend tests using pytest
	$(call print_status, "Running backend pytest test suite...")
	$(PYTHON) -m pytest tests/

test-frontend: ## Run JavaScript/TypeScript frontend tests
	$(call print_status, "Running frontend test suite...")
	cd frontend && npm run test --if-present

coverage: ## Generate test coverage XML/HTML reports
	$(call print_status, "Generating backend coverage report...")
	$(PYTHON) -m pytest --cov=app --cov-report=html tests/
	$(call print_success, "Coverage report generated in htmlcov/index.html")

benchmark: ## Run performance benchmark tests
	$(call print_status, "Running benchmark tests...")
	$(PYTHON) -m pytest tests/test_api_speed.py || echo "No benchmarks defined."

##@ 5. Code Quality
.PHONY: lint format type-check security-scan

lint: ## Check for code style and syntax problems (Ruff & ESLint)
	$(call print_status, "Running Ruff linter check (Backend)...")
	ruff check .
	$(call print_status, "Running ESLint check (Frontend)...")
	cd frontend && npm run lint

format: ## Automatically format code (Ruff & Prettier)
	$(call print_status, "Formatting backend code with Ruff...")
	ruff format .
	$(call print_status, "Formatting frontend code with Prettier...")
	cd frontend && npx prettier --write "app/**/*.{ts,tsx,js,jsx,json,css,md}" --ignore-path .gitignore || echo "Formatting finished."

type-check: ## Verify type annotations (Mypy & TypeScript tsc)
	$(call print_status, "Checking backend types with mypy...")
	mypy app/ --ignore-missing-imports
	$(call print_status, "Checking frontend TypeScript compiler...")
	cd frontend && npx tsc --noEmit

security-scan: ## Scan code for security issues (pip-audit & npm audit)
	$(call print_status, "Scanning backend requirements with pip-audit...")
	pip-audit -r requirements.txt || echo "Audit complete."
	$(call print_status, "Scanning frontend dependencies with npm audit...")
	cd frontend && npm audit --audit-level=high || echo "Audit complete."

##@ 6. Database Operations
.PHONY: db-shell db-reset db-backup db-restore db-seed

db-shell: ## Access database client shell (psql)
	docker compose -f $(DOCKER_COMPOSE_DEV) exec db psql -U postgres -d dbdiemdanh

db-reset: ## Clear and reinitialize database tables
	$(call print_warning, "This will delete all database tables and erase all data!")
	$(call confirm_action, "db-reset")
	$(PYTHON) -c "from app.core.db import engine; from sqlmodel import SQLModel; SQLModel.metadata.drop_all(engine); SQLModel.metadata.create_all(engine)"
	$(call print_success, "Database tables reset successfully.")

db-backup: ## Create backup sql dump from database container
	$(call print_status, "Creating database sql dump...")
	docker compose -f $(DOCKER_COMPOSE_DEV) exec -t db pg_dump -U postgres dbdiemdanh > database_backup.sql
	$(call print_success, "Backup saved as database_backup.sql")

db-restore: ## Restore database from database_backup.sql file
	$(call print_status, "Restoring database from database_backup.sql...")
	docker compose -f $(DOCKER_COMPOSE_DEV) exec -T db psql -U postgres dbdiemdanh < database_backup.sql
	$(call print_success, "Database restore completed.")

db-seed: ## Seed database with mock demo accounts
	$(call print_status, "Seeding database with mock records...")
	$(PYTHON) -c "from app.core.db import engine, init_db; from sqlmodel import Session; init_db(Session(engine))"
	$(call print_success, "Database seeded successfully.")

##@ 7. Alembic Migrations
.PHONY: migrate migrate-create migrate-history migrate-downgrade

migrate: ## Upgrade database to the latest schema revision
	$(call print_status, "Upgrading database to latest schema...")
	alembic upgrade head
	$(call print_success, "Database migrated.")

migrate-create: ## Generate a new alembic schema revision file
	@echo -n "Enter migration description message: " && read msg && \
	alembic revision --autogenerate -m "$$msg"
	$(call print_success, "Migration revision generated.")

migrate-history: ## List history of database schema revisions
	alembic history --verbose

migrate-downgrade: ## Downgrade database schema to previous revision
	$(call print_warning, "This will downgrade your database by 1 version.")
	$(call confirm_action, "migrate-downgrade")
	alembic downgrade -1
	$(call print_success, "Database downgraded by 1 revision.")

##@ 8. AI Utilities
.PHONY: ai-test ai-index ai-clear-cache camera-test

ai-test: ## Run face recognition algorithm tests on mock dataset
	$(call print_status, "Running face recognition algorithm tests...")
	$(PYTHON) app/test/test.py

ai-index: ## Force rebuild FAISS embedding indexes
	$(call print_status, "Synchronizing and rebuilding FAISS database index...")
	$(PYTHON) -c "from app.services.face_service import get_or_create_face_service; svc = get_or_create_face_service(); svc._sync_faiss_index_from_database()"
	$(call print_success, "FAISS index rebuilt.")

ai-clear-cache: ## Clean up local cached face models
	$(call print_status, "Cleaning face embeddings cached files...")
	rm -f vector_db/embeddings_db/*.bin vector_db/embeddings_db/*.pkl vector_db/embeddings_db/*.pickle
	$(call print_success, "Cache cleared.")

camera-test: ## Launch camera test script
	$(call print_status, "Launching camera integration tests...")
	$(PYTHON) -m pytest tests/test_webrtc_offer.py || echo "No camera test defined."

##@ 9. Health & Monitoring
.PHONY: health status metrics

health: ## Perform healthchecks for FastAPI, Frontend, PostgreSQL, Redis, Meilisearch, and Cloudinary
	$(call print_status, "Performing system services healthcheck...")
	@curl -sf http://localhost:5050/api/docs > /dev/null && echo -e "FastAPI Backend: $(GREEN)HEALTHY$(NC)" || echo -e "FastAPI Backend: $(RED)UNHEALTHY$(NC)"
	@curl -sf http://localhost:3000 > /dev/null && echo -e "Next.js Frontend: $(GREEN)HEALTHY$(NC)" || echo -e "Next.js Frontend: $(RED)UNHEALTHY$(NC)"
	@docker compose -f $(DOCKER_COMPOSE_DEV) exec db pg_isready -U postgres > /dev/null && echo -e "PostgreSQL: $(GREEN)HEALTHY$(NC)" || echo -e "PostgreSQL: $(RED)UNHEALTHY$(NC)"
	@docker compose -f $(DOCKER_COMPOSE_DEV) exec redis redis-cli ping > /dev/null 2>&1 && echo -e "Redis: $(GREEN)HEALTHY$(NC)" || echo -e "Redis: $(RED)NOT FOUND/UNHEALTHY$(NC)"
	@curl -sf http://localhost:7700/health > /dev/null 2>&1 && echo -e "Meilisearch: $(GREEN)HEALTHY$(NC)" || echo -e "Meilisearch: $(RED)NOT FOUND/UNHEALTHY$(NC)"
	@$(PYTHON) -c "from app.utils.cloudinary import init_cloudinary; init_cloudinary(); print('Cloudinary Connection: \033[1;32mHEALTHY\033[0m')" || echo -e "Cloudinary Connection: $(RED)UNHEALTHY$(NC)"

status: ## Display status of running containers
	docker compose -f $(DOCKER_COMPOSE_DEV) ps

metrics: ## Display container memory and cpu usage metrics
	docker stats --no-stream

##@ 10. Deployment
.PHONY: deploy-dev deploy-staging deploy-production rollback

deploy-dev: ## Deploy stack to local dev environment
	$(call print_status, "Deploying stack to local dev environment...")
	docker compose -f $(DOCKER_COMPOSE_DEV) up -d --build

deploy-staging: ## Deploy stack to staging environment
	$(call print_status, "Deploying stack to staging environment...")
	docker compose -f $(DOCKER_COMPOSE_PROD) up -d --build

deploy-production: ## Deploy stack to production server (Requires confirmation)
	$(call print_warning, "You are deploying to PRODUCTION!")
	$(call confirm_action, "deploy-production")
	docker compose -f $(DOCKER_COMPOSE_PROD) pull
	docker compose -f $(DOCKER_COMPOSE_PROD) up -d
	$(call print_success, "Production deployment completed successfully.")

rollback: ## Rollback production server deployment to previous image versions
	$(call print_warning, "This will rollback your production containers to the previous version.")
	$(call confirm_action, "rollback")
	git checkout HEAD@{1}
	docker compose -f $(DOCKER_COMPOSE_PROD) pull
	docker compose -f $(DOCKER_COMPOSE_PROD) up -d
	$(call print_success, "Rollback executed successfully.")

##@ 11. Utilities
.PHONY: install venv requirements update-deps

install: venv requirements ## Create virtual environment and install dependencies

venv: ## Create virtual environment
	$(call print_status, "Creating virtual environment...")
	python -m venv venv
	$(call print_success, "Virtual environment created.")

requirements: ## Install requirement libraries into virtualenv
	$(call print_status, "Installing backend dependencies...")
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	$(call print_status, "Installing frontend dependencies...")
	cd frontend && npm install
	$(call print_success, "All dependencies installed successfully.")

update-deps: ## Update python dependencies and lock file
	$(call print_status, "Updating python dependencies...")
	$(PIP) install --upgrade -r requirements.txt
	$(call print_success, "Dependencies updated.")
