# Project settings
PROJECT_NAME := news-app

# Default tag is formatted as date-commit_hash
TAG := $(shell date +%Y%m%d)-$(shell git rev-parse --short HEAD 2>/dev/null || echo 'dev')

.PHONY: help dev-up dev-down dev-build dev-logs dev-all dev-restart prod-build prod-deploy prod-remove prod-all prod-status prod-logs prod-secrets-remove clean validate

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Development commands
dev-build: ## Build development containers
	docker compose -f compose.base.yml -f compose.yml build

dev-up: ## Start development environment
	@if [ -z "$(GEMINI_API_KEY)" ]; then \
		echo "GEMINI_API_KEY is not set"; \
		read -p "Enter your GEMINI_API_KEY: " input_key; \
		sed -i.bak "s|GEMINI_API_KEY=.*|GEMINI_API_KEY=$$input_key|" envs/common_dev.env; \
	fi
	docker compose -f compose.base.yml -f compose.yml up -d

dev-down: ## Stop development environment
	docker compose -f compose.base.yml -f compose.yml down

dev-logs: ## Show logs from development containers
	docker compose -f compose.base.yml -f compose.yml logs -f

dev-restart: ## Restart development environment
	$(MAKE) dev-down
	$(MAKE) dev-up

dev-all: dev-build dev-up ## Build and start complete development environment

# Production commands
prod-build: ## Build production images
	docker compose -f compose.base.yml -f compose.prod.yml build
	@echo "Built production images"

prod-deploy: ## Deploy to production (Docker Swarm)
	@echo "Deploying to production..."
	@if ! docker secret ls | grep -q "db_password"; then \
		read -s -p "Database password: " DB_PASSWORD && echo && \
		echo $$DB_PASSWORD | docker secret create db_password - ; \
		echo "Created database password secret"; \
	fi
	@if ! docker secret ls | grep -q "gemini_api_key"; then \
		read -s -p "Gemini API key: " GEMINI_KEY && echo && \
		echo $$GEMINI_KEY | docker secret create gemini_api_key - ; \
		echo "Created Gemini API key secret"; \
	fi
	docker stack deploy -c compose.base.yml -c compose.prod.yml $(PROJECT_NAME)
	@echo "Production deployment complete"

prod-status: ## Show production stack status
	docker stack services $(PROJECT_NAME)
	docker stack ps $(PROJECT_NAME)

prod-logs: ## Show production logs
	docker service logs $(PROJECT_NAME)_backend
	docker service logs $(PROJECT_NAME)_frontend

prod-remove: ## Remove production stack
	docker stack rm $(PROJECT_NAME)
	@echo "Production stack removed"

prod-secrets-remove: ## Remove production secrets (use with caution)
	@echo "Warning: This will remove all secrets!"
	@read -p "Are you sure? [y/N]: " confirm && [ "$$confirm" = "y" ] || exit 1
	docker secret rm db_password gemini_api_key || true

prod-all: prod-build prod-deploy ## Build and deploy complete production environment

# Utility commands
clean: ## Clean up unused Docker resources
	docker system prune -f
	docker volume prune -f

validate: ## Validate Docker Compose configurations
	@echo "Validating development configuration..."
	docker compose -f compose.base.yml -f compose.yml config >/dev/null
	@echo "✓ Development configuration is valid"
	@echo "Validating production configuration..."
	docker compose -f compose.base.yml -f compose.prod.yml config >/dev/null
	@echo "✓ Production configuration is valid"