APP ?= $(HEROKU_APP_NAME)

.DEFAULT_GOAL := help

# ── Help ──────────────────────────────────────────────────────────────────────

.PHONY: help
help: ## Show this help
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} \
	/^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-24s\033[0m %s\n", $$1, $$2 } \
	/^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) }' $(MAKEFILE_LIST)

# ── Setup ─────────────────────────────────────────────────────────────────────

##@ Setup

.PHONY: setup
setup: config.json .env ## Copy example config files (skips if already exist)

config.json:
	cp config.example.json config.json
	@echo "Created config.json — edit it before running"

.env:
	cp .env.example .env
	@echo "Created .env — fill in secrets before running"

.PHONY: install
install: ## Install Python dependencies locally
	pip install -r requirements.txt

# ── Docker ────────────────────────────────────────────────────────────────────

##@ Docker

.PHONY: build
build: ## Build Docker image
	docker compose build

.PHONY: up
up: ## Start bot + postgres in background
	docker compose up -d

.PHONY: down
down: ## Stop and remove containers
	docker compose down

.PHONY: down-v
down-v: ## Stop containers and delete postgres volume
	docker compose down -v

.PHONY: restart
restart: ## Restart the bot container
	docker compose restart bot

.PHONY: logs
logs: ## Tail bot logs
	docker compose logs -f bot

.PHONY: ps
ps: ## Show container status
	docker compose ps

.PHONY: shell
shell: ## Open a shell inside the bot container
	docker compose exec bot bash

# ── Development ───────────────────────────────────────────────────────────────

##@ Development

.PHONY: run
run: ## Run bot locally (requires local .env and config.json)
	python -m bot.main

.PHONY: test
test: ## Run full test suite
	pytest tests/ -v

.PHONY: test-fast
test-fast: ## Run tests (quiet output)
	pytest tests/ -q

# ── Scripts ───────────────────────────────────────────────────────────────────

##@ Scripts (run inside Docker container)

.PHONY: db-stats
db-stats: ## Show database table stats
	docker compose exec bot python scripts/db_stats.py

.PHONY: export-db
export-db: ## Export database tables to CSV
	docker compose exec bot python scripts/export_db.py

.PHONY: wallet-history
wallet-history: ## Show positions, trades, and balances
	docker compose exec bot python scripts/wallet_history.py

# ── Heroku ────────────────────────────────────────────────────────────────────

##@ Heroku  (set APP=<name> or export HEROKU_APP_NAME)

.PHONY: heroku-start
heroku-start: ## Scale web dyno to 1 (start bot)
	./alive.sh $(APP)

.PHONY: heroku-stop
heroku-stop: ## Scale all dynos to 0 (stop bot)
	./kill.sh $(APP)

.PHONY: heroku-logs
heroku-logs: ## Tail and pretty-print Heroku logs
	./logs.sh $(APP)

.PHONY: heroku-logs-raw
heroku-logs-raw: ## Tail raw Heroku logs
	./logs.sh raw $(APP)

.PHONY: heroku-live-enable
heroku-live-enable: ## Enable live order transmission on Heroku
	./live_enabled.sh $(APP)

.PHONY: heroku-live-disable
heroku-live-disable: ## Disable live order transmission on Heroku
	./live_disabled.sh $(APP)
