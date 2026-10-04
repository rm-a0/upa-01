.DEFAULT_GOAL := help

ZIP_NAME     ?= submission.zip
SUBMIT_FILES := urls.txt data.tsv get_urls.py scraper.py build.sh run.sh README.md requirements.txt

.PHONY: help setup lint format typecheck requirements build run zip clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

setup: ## Install deps with uv (local development)
	uv sync

# --- Code quality ---
lint: ## Check formatting and lint rules
	uv run ruff check .
	uv run ruff format --check .

format: ## Auto-format code
	uv run ruff format .

typecheck: ## Run mypy
	uv run mypy .

# --- Build and Run ---
requirements: ## Export requirements.txt from uv.lock
	uv export --format requirements-txt --no-hashes --no-dev --no-emit-project -o requirements.txt

build: ## Run build.sh (venv + pip, as on merlin)
	./build.sh

run: ## Run run.sh (collect URLs, scrape first 10)
	./run.sh

# --- Submission ---
zip: requirements ## Build the submission archive ($(ZIP_NAME))
	@for f in $(SUBMIT_FILES); do \
		[ -f "$$f" ] || { echo "Missing required file: $$f" >&2; exit 1; }; \
	done
	@rm -f $(ZIP_NAME)
	python3 -m zipfile -c $(ZIP_NAME) $(SUBMIT_FILES)
	@python3 -m zipfile -l $(ZIP_NAME)

clean: ## Remove caches and build artifacts
	rm -rf .pytest_cache .ruff_cache .mypy_cache dist build url_test.txt $(ZIP_NAME)
	find . -type d -name __pycache__ -exec rm -rf {} +
