# Project settings
PROJECT_NAME := app

# Default tag is formatted as date-commit_hash
TAG := $(shell date +%Y%m%d)-$(shell git rev-parse --short HEAD 2>/dev/null || echo 'dev')

.PHONY: help dev-up dev-down dev-build dev-logs dev-all prod-build prod-deploy prod-remove prod-all

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

dev-up: ## Start development environment
	@if [ -z "$(GEMINI_API_KEY)" ]; then \
		echo "GEMINI_API_KEY is not set"; \
		read -p "Enter your GEMINI_API_KEY: " input_key; \
		GEMINI_API_KEY=$$input_key docker compose -f docker-compose.base.yml -f docker-compose.dev.yml up -d; \
	else \
		echo "Using existing GEMINI_API_KEY: $(GEMINI_API_KEY)"; \
		GEMINI_API_KEY=$(GEMINI_API_KEY) docker compose -f docker-compose.base.yml -f docker-compose.dev.yml up -d; \
	fi

dev-down: ## Stop development environment
	docker compose -f docker-compose.base.yml -f docker-compose.dev.yml down

dev-build: ## Rebuild development containers
	docker compose -f docker-compose.base.yml -f docker-compose.dev.yml build

dev-logs: ## Show logs from all containers
	docker compose -f docker-compose.base.yml -f docker-compose.dev.yml logs -f

dev-all: dev-build dev-up ## Build and start development environment

# Production commands
prod-build: ## Build production images
	TAG=$(TAG) docker compose -f docker-compose.base.yml -f docker-compose.prod.yml build
	@echo "Built with tag: $(TAG)"

prod-deploy: ## Deploy to production (Docker Swarm)
	@echo "Deploying version $(TAG) to production..."
	@if ! docker secret ls | grep -q "db_password"; then \
		read -p "Database password: " DB_PASSWORD && \
		echo $$DB_PASSWORD | docker secret create db_password - ; \
	fi
	@if ! docker secret ls | grep -q "gemini_api_key"; then \
		read -p "Gemini API key: " GEMINI_KEY && \
		echo $$GEMINI_KEY | docker secret create gemini_api_key - ; \
	fi
	TAG=$(TAG) docker stack deploy -c docker-compose.base.yml -c docker-compose.prod.yml $(PROJECT_NAME)

prod-remove: ## Remove production stack
	docker stack rm $(PROJECT_NAME)

prod-all: prod-build prod-deploy ## Build and deploy to production