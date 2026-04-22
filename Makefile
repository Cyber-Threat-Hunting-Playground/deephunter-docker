.PHONY: help build up down restart logs shell db-shell backup restore clean init status health check-requirements validate-config monitor upgrade diagnostics download-deephunter logs-cron setup-hooks

# Load .env variables (if present) so targets can reference GITHUB_REPO, DEEPHUNTER_VERSION, etc.
-include .env
export

GITHUB_REPO  ?= Cyber-Threat-Hunting-Playground/deephunter
DEEPHUNTER_VERSION ?= 2.5
ENABLE_CRON  ?= false

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

# Default target
.DEFAULT_GOAL := help

help: ## Show this help message
	@echo "$(BLUE)DeepHunter Docker Management$(NC)"
	@echo ""
	@echo "$(GREEN)Available commands:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-15s$(NC) %s\n", $$1, $$2}'
	@echo ""

build: ## Build DeepHunter Docker image
	@echo "$(BLUE)Building DeepHunter image...$(NC)"
	./build.sh
	@echo "$(GREEN)Build complete!$(NC)"

download-deephunter: ## Download DeepHunter source for offline build (use if build fails at DOWNLOADING DEEPHUNTER)
	@echo "$(BLUE)Downloading DeepHunter v$(DEEPHUNTER_VERSION) from $(GITHUB_REPO)...$(NC)"
	@mkdir -p resources
	@curl -L -o resources/v$(DEEPHUNTER_VERSION).tar.gz https://github.com/$(GITHUB_REPO)/archive/refs/tags/v$(DEEPHUNTER_VERSION).tar.gz
	@echo "$(GREEN)Download complete! Run 'make build' to build with bundled source.$(NC)"

check-requirements: ## Check system requirements
	@chmod +x scripts/check-requirements.sh
	./scripts/check-requirements.sh

up: ## Start all services
	@echo "$(BLUE)Starting DeepHunter services...$(NC)"
	@mkdir -p data/redis data/logs data/backups
	@# Remove stale app container(s) to avoid 'ContainerConfig' KeyError on recreate
	@# (docker compose 1.x bug). Bind-mounted data is preserved.
	@docker ps -aq --filter "name=deephunter-app" | xargs -r docker rm -f 2>/dev/null || true
	docker compose up -d
	@echo "$(GREEN)Services started!$(NC)"
ifeq ($(ENABLE_CRON),true)
	@echo "$(GREEN)Cron orchestrator enabled (see CRON_SCHEDULE in .env)$(NC)"
else
	@echo "$(YELLOW)Cron orchestrator disabled. Set ENABLE_CRON=true in .env to enable.$(NC)"
endif
	@echo "$(YELLOW)Run 'make init' for first-time setup$(NC)"

down: ## Stop all services
	@echo "$(BLUE)Stopping DeepHunter services...$(NC)"
	docker compose down
	@echo "$(GREEN)Services stopped!$(NC)"

restart: down up ## Restart all services

logs: ## Show logs from all services
	docker compose logs -f

logs-filter: ## Filter logs (usage: make logs-filter SERVICE=app FILTER=error)
	@chmod +x scripts/logs.sh
	./scripts/logs.sh $(SERVICE) $(FILTER)

logs-app: ## Show logs from DeepHunter application only
	docker compose logs -f deephunter

logs-db: ## Show logs from MariaDB only
	docker compose logs -f mariadb

logs-redis: ## Show logs from Redis only
	docker compose logs -f redis

logs-cron: ## Show orchestrator cron execution logs
	@if [ -f data/logs/cron-orchestrator.log ]; then \
		tail -f data/logs/cron-orchestrator.log; \
	else \
		echo "$(YELLOW)No cron log yet. Set ENABLE_CRON=true in .env and run 'make restart'.$(NC)"; \
	fi

shell: ## Open shell in DeepHunter container
	@echo "$(BLUE)Opening shell in DeepHunter container...$(NC)"
	docker exec -it deephunter-app bash

db-shell: ## Open MariaDB shell
	@echo "$(BLUE)Opening MariaDB shell...$(NC)"
	@docker exec -it deephunter-mariadb mariadb -u deephunter -p

redis-shell: ## Open Redis CLI
	@echo "$(BLUE)Opening Redis CLI...$(NC)"
	docker exec -it deephunter-redis redis-cli

init: ## Initialize DeepHunter (first time setup)
	@echo "$(BLUE)Initializing DeepHunter...$(NC)"
	@if ! docker inspect -f '{{.State.Running}}' deephunter-app 2>/dev/null | grep -q true; then \
		echo "$(YELLOW)App container is not running; starting services (make up)...$(NC)"; \
		$(MAKE) up || exit 1; \
		echo "$(YELLOW)Waiting for stack to settle (DB + app)...$(NC)"; \
		sleep 15; \
	fi
	@chmod +x scripts/init-deephunter.sh
	./scripts/init-deephunter.sh
	@echo "$(GREEN)Initialization complete!$(NC)"

status: ## Show status of all services
	@echo "$(BLUE)Service Status:$(NC)"
	@docker compose ps

health: ## Check health of all services
	@echo "$(BLUE)Health Status:$(NC)"
	@docker ps --filter "name=deephunter" --format "table {{.Names}}\t{{.Status}}"

monitor: ## Monitor performance (usage: make monitor INTERVAL=5)
	@chmod +x scripts/monitor.sh
	./scripts/monitor.sh $(INTERVAL)

diagnostics: ## Generate diagnostic report for troubleshooting
	@echo "$(BLUE)Generating diagnostics...$(NC)"
	@chmod +x scripts/diagnostics.sh
	./scripts/diagnostics.sh

backup: ## Backup database and data
	@echo "$(BLUE)Creating backup...$(NC)"
	@chmod +x scripts/backup.sh
	./scripts/backup.sh
	@echo "$(GREEN)Backup complete!$(NC)"

restore: ## Restore from backup (use BACKUP_FILE=path/to/backup.tar.gz)
	@echo "$(BLUE)Restoring from backup...$(NC)"
	@chmod +x scripts/restore.sh
	./scripts/restore.sh $(BACKUP_FILE)

clean: ## Remove all containers, volumes, and data (WARNING: destructive!)
	@echo "$(RED)WARNING: This will remove all data!$(NC)"
	@printf "Are you sure? [y/N] " && read REPLY && \
	case "$$REPLY" in \
		[Yy]*) \
			docker compose down -v; \
			rm -rf data/redis/* data/logs/* data/backups/*; \
			echo "$(GREEN)Cleanup complete!$(NC)";; \
		*) \
			echo "$(YELLOW)Cancelled.$(NC)";; \
	esac

rebuild: clean build up ## Clean rebuild everything

update: ## Update DeepHunter to latest version
	@echo "$(BLUE)Updating DeepHunter...$(NC)"
	docker compose pull
	$(MAKE) down
	$(MAKE) build
	$(MAKE) up
	@echo "$(GREEN)Update complete!$(NC)"

upgrade: ## Upgrade with automatic backup and health checks
	@chmod +x scripts/upgrade.sh
	./scripts/upgrade.sh

env: ## Create .env file from template
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "$(GREEN).env file created! Please edit it with your settings.$(NC)"; \
	else \
		echo "$(YELLOW).env file already exists.$(NC)"; \
	fi

validate: ## Validate docker compose configuration
	@echo "$(BLUE)Validating configuration...$(NC)"
	docker compose config --quiet && echo "$(GREEN)Configuration is valid!$(NC)" || echo "$(RED)Configuration has errors!$(NC)"

validate-config: ## Validate settings.py configuration
	@chmod +x scripts/validate-config.sh
	./scripts/validate-config.sh

setup-hooks: ## Configure git hooks and forbidden-string patterns
	@git config core.hooksPath .githooks
	@chmod +x .githooks/pre-commit .githooks/pre-push 2>/dev/null || true
	@if [ ! -f .githooks/forbidden-patterns.txt ] && [ -f .githooks/forbidden-patterns.txt.example ]; then \
		cp .githooks/forbidden-patterns.txt.example .githooks/forbidden-patterns.txt; \
		echo "$(GREEN)Created .githooks/forbidden-patterns.txt from example template.$(NC)"; \
	fi
	@echo "$(GREEN)Git hooks activated (core.hooksPath = .githooks).$(NC)"

install: env setup-hooks build up init ## Complete installation (build, start, and initialize)
	@echo "$(GREEN)DeepHunter installation complete!$(NC)"
	@echo "$(BLUE)Access DeepHunter at: https://localhost:9000$(NC)"

pre-install-check: check-requirements ## Run pre-installation checks
	@echo "$(GREEN)Pre-installation checks complete!$(NC)"
	@echo "$(BLUE)Run 'make install' to proceed with installation$(NC)"
