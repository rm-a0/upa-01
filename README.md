# UPA Project 1

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
