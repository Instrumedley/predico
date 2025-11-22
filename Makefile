.PHONY: help install dev build test clean docker-up docker-down migrate

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install dependencies for backend and frontend
	cd backend && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt
	cd frontend && npm install

dev-backend: ## Run backend in development mode
	cd backend && source venv/bin/activate && uvicorn app.main:app --reload

dev-frontend: ## Run frontend in development mode
	cd frontend && npm run dev

dev: ## Run both backend and frontend in development mode
	docker-compose up

build: ## Build Docker images
	docker-compose build

docker-up: ## Start all services with Docker Compose
	docker-compose up -d

docker-down: ## Stop all services
	docker-compose down

docker-logs: ## View Docker Compose logs
	docker-compose logs -f

migrate: ## Run database migrations
	cd backend && source venv/bin/activate && alembic upgrade head

migrate-create: ## Create a new migration (usage: make migrate-create MESSAGE="description")
	cd backend && source venv/bin/activate && alembic revision --autogenerate -m "$(MESSAGE)"

test-backend: ## Run backend tests
	cd backend && source venv/bin/activate && pytest

test-frontend: ## Run frontend tests
	cd frontend && npm test

lint-backend: ## Lint backend code
	cd backend && source venv/bin/activate && black . && flake8 .

lint-frontend: ## Lint frontend code
	cd frontend && npm run lint

clean: ## Clean up generated files
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -r {} +
	cd frontend && rm -rf node_modules dist

terraform-init: ## Initialize Terraform
	cd infrastructure/terraform && terraform init

terraform-plan: ## Plan Terraform changes
	cd infrastructure/terraform && terraform plan

terraform-apply: ## Apply Terraform changes
	cd infrastructure/terraform && terraform apply

terraform-destroy: ## Destroy Terraform infrastructure
	cd infrastructure/terraform && terraform destroy

