# Project settings
PROJECT_NAME := app

# Default tag is formatted as date-commit_hash
TAG := $(shell date +%Y%m%d)-$(shell git rev-parse --short HEAD 2>/dev/null || echo 'dev')

.PHONY: help dev-up dev-down dev-build dev-logs prod-build prod-deploy prod-remove prod-all prod-deploy-simple

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

dev-up: ## Start development environment
	@if [ -z "$(GEMINI_API_KEY)" ]; then \
		echo "GEMINI_API_KEY is not set"; \
		read -p "Enter your GEMINI_API_KEY: " input_key; \
		GEMINI_API_KEY=$$input_key docker compose -f compose.base.yml -f compose.yml up -d; \
	else \
		echo "Using existing GEMINI_API_KEY: $(GEMINI_API_KEY)"; \
		GEMINI_API_KEY=$(GEMINI_API_KEY) docker compose -f compose.base.yml -f compose.yml up -d; \
	fi

dev-down: ## Stop development environment
	docker compose -f compose.base.yml -f compose.yml down

dev-build: ## Rebuild development containers
	docker compose -f compose.base.yml -f compose.yml build

dev-logs: ## Show logs from all containers.
	docker compose -f compose.base.yml -f compose.yml logs -f

# Production commands
prod-build: ## Build production images
	docker compose -f compose.base.yml -f compose.prod.yml build
	@echo "Built production images"

prod-deploy: ## Deploy to production using Docker Compose
	@echo "Deploying to production..."
	@if [ ! -f .env ]; then \
		echo "Creating .env file from template..."; \
		cp .env.example .env; \
		echo "Please edit .env file with your production values and run again"; \
		exit 1; \
	fi
	docker compose -f compose.base.yml -f compose.prod.yml up -d

prod-remove: ## Remove production stack
	docker compose -f compose.base.yml -f compose.prod.yml down

prod-all: prod-build prod-deploy ## Build and deploy to production

prod-deploy-simple: ## Simple production deployment (uses deploy.sh)
	./deploy.sh
