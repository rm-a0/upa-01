# UPA Projects 1 and 2

## Team

- Team: xrepcim00
- Solvers: xrepcim00, xvesela00

## E-shop

The project uses the foreign e-shop [Knivesandtools](https://www.knivesandtools.com/),
specifically its flashlight category:
https://www.knivesandtools.com/en/ct/flashlights.htm

The URL collector selects comparable flashlight products from this category. It
walks category pages and prints up to 200 unique product URLs to standard output.

## Programs

Build the virtual environment with:

```sh
./build.sh
```

Collect the URL sample with Make:

```sh
make urls
```

Collect the complete product dataset with Make:

```sh
make data
```

`make data` first regenerates `urls.txt`, then scrapes every URL into
`data.tsv`. It takes time because requests are separated by a two-second delay.
The assignment's required smoke test remains available as:

```sh
make run
```

The scraper makes no API requests. It reads the HTML product pages and their
embedded structured data or specification markup.

## TSV columns

There is no header row. Every row has these columns, in order:

| # | Column | Example |
|---|---|---|
| 1 | Product URL | `https://www.knivesandtools.com/en/pt/-fenix-c7-...htm` |
| 2 | Product name | `Fenix C7 rechargeable flashlight, 3000 lumens, orange` |
| 3 | Current selling price (EUR, without currency symbol) | `79.95` |
| 4 | Brand | `Fenix` |
| 5 | Colour | `orange` |
| 6 | Length | `14.9 cm` |
| 7 | Weight | `172 g` |
| 8 | Material | `aluminum` |
| 9 | Maximum light intensity | `3,000 lumens` |

All values remain strings as displayed by the shop. If a product does not list a
parameter, the corresponding field is empty. If a product page cannot be
downloaded, its row contains only the URL and empty fields.

Notes:

- The price comes from the page's embedded JSON-LD (`offers.price`) and is the
  current price, including discounts.
- Colour and Material can contain several comma-separated values, e.g.
  `aluminum, carbon fiber, composite`.

## robots.txt and request precautions

`robots.txt` allows all paths for the default user agent except `/cart`,
`/checkout`, `/account` and `/*/compare`. Measures taken:

- only the category listing (`/en/ct/flashlights.htm?p=N`) and product pages
  (`/en/pt/*.htm`) are requested, both allowed
- a 2 s delay before every request (no `Crawl-delay` is set, we add one anyway)
- one sequential connection, no parallel requests
- a descriptive User-Agent with contact e-mails
- retries only for temporary errors (429, 5xx), with backoff
- the URL collector stops as soon as it has 200 URLs or a page adds nothing new

## Test run

```sh
./run.sh
```

This writes the collected URLs to `url_test.txt` and sends the first ten
scraped rows to standard output.

## Project 2: exploratory analysis and data preparation

The second part of the project uses the dataset from `data.tsv` and prepares two
variants for price prediction. The source code is in `analysis/`:

| File | Purpose |
|---|---|
| `analysis/load.py` | Shared loader; parses `data.tsv` into a typed dataframe |
| `analysis/eda.ipynb` | Exploratory analysis, outliers, missing values, correlations |
| `analysis/prep.ipynb` | Creates the two prepared datasets |
| `analysis/data_categorical.csv` | Variant A: all attributes categorical (price classes) |
| `analysis/data_numeric.csv` | Variant B: all attributes numeric in `[0, 1]` (price regression) |
| `docs/documentation.pdf` | Project documentation with the required figures and tables |

The mining task is supervised **price prediction**. Variant A turns price into
three quantile-based classes (`low`, `mid`, `high`) and discretizes the numeric
predictors. Variant B keeps price numeric, applies `log1p` to the numeric
predictors, one-hot encodes the categorical attributes and normalizes all
columns to `[0, 1]`. The identifier columns `url` and `name` and the nearly
constant `colour` attribute are dropped; `material` is kept. Both variants also
contain a binary `bundle` flag derived from the product name. It marks kits,
packs, holsters, cables, battery systems and listings with attachments without
removing those rows.

Outliers are detected and documented but not removed or capped because they are
valid premium/large products. Variant A's quantile bins and variant B's log
transformation limit their influence.

### Running the analysis

The analysis dependencies are included in `requirements.txt` and
`pyproject.toml`. With `uv`, install the environment with:

```sh
uv sync
```

Then open the notebooks in `analysis/` in Jupyter and run them in order:
`eda.ipynb` first, then `prep.ipynb`. The preparation notebook writes the two
CSV files into `analysis/`.

Alternatively, execute the notebooks from the command line with `nbconvert`.
The first command registers the project environment as a Jupyter kernel, so the
notebooks use exactly the dependencies installed by `uv`:

```sh
uv run python -m ipykernel install --user --name upa-venv --display-name "UPA project venv"
uv run --with nbconvert jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.kernel_name=upa-venv analysis/eda.ipynb analysis/prep.ipynb
```

The documentation PDF can be rebuilt with:

```sh
make docs
```

If the EDA plots changed, refresh the figures from `eda.ipynb` first:

```sh
make figures
```

`make report` runs both steps (`figures` and `docs`).

The submission archive is built with `make zip2`. It contains the analysis
source, both prepared CSVs, the documentation PDF and `data.tsv`.
