# UPA Project 1

## Team

- Team: UPA project 1
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

1. Product URL
2. Product name
3. Current selling price
4. Brand
5. Colour
6. Length
7. Weight
8. Material
9. Maximum light intensity

All values remain strings as displayed by the shop. If a product does not list a
parameter, the corresponding field is empty.

## robots.txt and request precautions

The analyzed `robots.txt` allows all paths for the default user agent except
`/cart`, `/checkout`, `/account`, and paths matching `/*/compare`. The
implementation requests only the selected category and product pages, waits two
seconds between requests, uses a descriptive User-Agent, performs no parallel
crawling, and retries only temporary server errors. The current command-line
environment can receive a Cloudflare 403 response even though the pages are
available in a browser; sample datasets should therefore be generated from an
execution environment with permitted access.

## Test run

```sh
./run.sh
```

This writes the collected URLs to `url_test.txt` and sends the first ten
scraped rows to standard output.
