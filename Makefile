.DEFAULT_GOAL := help

# Submission archive, override with: make zip2 ZIP=other.zip
ZIP ?= xrepcim00.zip

PART1 := README.md requirements.txt build.sh run.sh \
         urls.txt data.tsv $(wildcard src/*.py)

PART2 := README.md Makefile requirements.txt pyproject.toml data.tsv \
         $(wildcard analysis/*.py) $(wildcard analysis/*.ipynb) \
         analysis/data_categorical.csv analysis/data_numeric.csv \
         docs/documentation.pdf docs/documentation.tex \
         $(wildcard docs/figures/*.png)

.PHONY: help setup lint format typecheck requirements \
        build urls data run notebooks figures docs report zip1 zip2 clean

help: ## Show this help
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

# --- Development ---
setup: ## Install dependencies with uv
	uv sync

lint: ## Check lint rules and formatting
	uv run ruff check .
	uv run ruff format --check .

format: ## Fix lint errors and format code
	uv run ruff check --fix .
	uv run ruff format .

typecheck: ## Run mypy
	uv run mypy src

requirements: ## Export requirements.txt from uv.lock
	uv export --format requirements-txt --no-hashes --no-dev --no-emit-project -o requirements.txt

# --- Part 1: scraping ---
build: ## Create .venv with build.sh
	./build.sh

urls: build ## Collect product URLs into urls.txt
	.venv/bin/python src/get_urls.py > urls.txt

data: urls ## Scrape every URL into data.tsv
	.venv/bin/python src/scraper.py < urls.txt > data.tsv

run: build ## Smoke test with run.sh
	./run.sh

# --- Part 2: analysis ---
notebooks: ## Run both notebooks, writes the CSVs
	uv run --with nbconvert jupyter nbconvert --to notebook --execute --inplace analysis/eda.ipynb analysis/prep.ipynb

figures: ## Run the EDA notebook and export its figures
	uv run --with nbconvert jupyter nbconvert --to notebook --execute --inplace analysis/eda.ipynb
	uv run python analysis/export_figures.py

docs: ## Build docs/documentation.pdf
	cd docs && pdflatex -interaction=nonstopmode -halt-on-error documentation.tex
	cd docs && pdflatex -interaction=nonstopmode -halt-on-error documentation.tex

report: figures docs ## Refresh figures, then build the PDF

# --- Submission ---
zip1: FILES = $(PART1)
zip2: FILES = $(PART2)

zip1: ## Build the part-1 archive
zip2: ## Build the part-2 archive

zip1 zip2: requirements
	@for f in $(FILES); do [ -f "$$f" ] || { echo "Missing file: $$f" >&2; exit 1; }; done
	@rm -f $(ZIP)
	@# Not "python3 -m zipfile -c", it flattens directories.
	@python3 -c 'import sys, zipfile; z = zipfile.ZipFile(sys.argv[1], "w", zipfile.ZIP_DEFLATED); [z.write(f) for f in sys.argv[2:]]; z.close()' $(ZIP) $(FILES)
	@python3 -m zipfile -l $(ZIP)

clean: ## Remove caches and build artifacts
	rm -rf .pytest_cache .ruff_cache .mypy_cache dist build url_test.txt
	find . -type d -name __pycache__ -exec rm -rf {} +
