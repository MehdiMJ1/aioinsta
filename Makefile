MESSAGE = "auto"


all: help

test: test-api ## Run all project tests
	@echo "Run all project tests"

test-api: ## Run api tests
	@echo "Run api tests"
	pytest

collect-requirements: ## Collect all python requirements
	@echo "Collect all python requirements"
	pip freeze > requirements.txt

migrate: ## Generate new migration by changes between schema and db
	@echo "Generate new migration by changes between schema and db"
	python api/db/migrations/ revision --autogenerate -m $(MESSAGE)

upgrade: ## Upgrade db up to 1 migration
	@echo "Upgrade db up to 1 migration"
	python api/db/migrations/ upgrade +1

upgrade-all: ## Upgrade db up to date
	@echo "Upgrade db up to date"
	python api/db/migrations/ upgrade head

downgrade: ## Downgrade db down to 1 migration
	@echo "Downgrade db down to 1 migration"
	python api/db/migrations/ downgrade -1

downgrade-all: ## Downgrade db to base state
	@echo "Downgrade db to base state"
	python api/db/migrations/ downgrade base

run-api: ## Run API application
	@echo "Run API application"
	python api/

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: help