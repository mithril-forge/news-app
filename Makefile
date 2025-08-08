# Interpret the rest of the arguments after first target as arguments to some command, e.g.:
# - `make logs backend` will execute `docker compose logs -f backend`
# - to use optional args, use `--` to separate them from make
RUN_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
$(eval $(RUN_ARGS):;@:)

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

up: ## Start development environment
	docker compose up -d

down: ## Stop and remove all dev containers
	docker compose down --remove-orphans

build: ## Rebuild development containers
	docker compose build

logsall: ## Show logs from all containers
	docker compose logs -f

logs: ## Show logs from specified container (e.g. `make logs backend`)
	docker compose logs -f

ruff: ## Run ruff check on backend and attempt to fix issues
	$(MAKE) -C backend ruff

format: ## Format backend code with ruff
	$(MAKE) -C backend ruff-format

mypy: ## Run mypy type checking on backend
	$(MAKE) -C backend check-mypy
