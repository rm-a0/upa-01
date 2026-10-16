.DEFAULT_GOAL := help

ZIP_NAME     ?= submission.zip
REQUIRED     := urls.txt data.tsv src/get_urls.py src/scraper.py build.sh run.sh README.md requirements.txt
SUBMIT_FILES  = $(sort $(REQUIRED) $(wildcard src/*.py))

.PHONY: help setup lint format typecheck requirements build urls data run zip clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

setup: ## Install deps with uv (local development)
	uv sync

# --- Code quality ---
lint: ## Check formatting and lint rules
	uv run ruff check .
	uv run ruff format --check .

format: ## Auto-fix lint errors and format code
	uv run ruff check --fix .
	uv run ruff format .

typecheck: ## Run mypy
	uv run mypy src

# --- Build and Run ---
requirements: ## Export requirements.txt from uv.lock
	uv export --format requirements-txt --no-hashes --no-dev --no-emit-project -o requirements.txt

build: ## Run build.sh (venv + pip, as on merlin)
	./build.sh

urls: build ## Collect the product URL sample into urls.txt
	.venv/bin/python src/get_urls.py > urls.txt

data: build urls ## Scrape every URL in urls.txt into data.tsv
	.venv/bin/python src/scraper.py < urls.txt > data.tsv

run: build ## Run run.sh (collect URLs, scrape first 10)
	./run.sh

# --- Submission ---
zip: requirements ## Build the submission archive ($(ZIP_NAME))
	@for f in $(REQUIRED); do \
		[ -f "$$f" ] || { echo "Missing required file: $$f" >&2; exit 1; }; \
	done
	@rm -f $(ZIP_NAME)
	@# Not "python3 -m zipfile -c": it drops directories (src/ would be flattened).
	python3 -c 'import sys, zipfile; z = zipfile.ZipFile(sys.argv[1], "w", zipfile.ZIP_DEFLATED); [z.write(f) for f in sys.argv[2:]]; z.close()' $(ZIP_NAME) $(SUBMIT_FILES)
	@python3 -m zipfile -l $(ZIP_NAME)

clean: ## Remove caches and build artifacts
	rm -rf .pytest_cache .ruff_cache .mypy_cache dist build url_test.txt $(ZIP_NAME)
	find . -type d -name __pycache__ -exec rm -rf {} +
