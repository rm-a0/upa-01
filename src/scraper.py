import json
import logging
import re
import sys
from collections.abc import Iterable
from typing import Any

from bs4 import BeautifulSoup

from common import fetch

logger = logging.getLogger(__name__)

PARAMETERS = (
    "Brand",
    "Colour",
    "Length",
    "Weight",
    "Material",
    "Maximum light intensity",
)


def clean(value: str) -> str:
    """Keep one TSV-safe, human-readable value."""
    return re.sub(r"\s+,", ",", re.sub(r"\s+", " ", value)).strip()


def json_values(value: Any) -> Iterable[dict[str, Any]]:
    """Yield JSON objects recursively, including objects inside @graph."""
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from json_values(child)
    elif isinstance(value, list):
        for child in value:
            yield from json_values(child)


def product_json(soup: BeautifulSoup) -> dict[str, Any]:
    for script in soup.select('script[type="application/ld+json"]'):
        try:
            data = json.loads(script.string or script.get_text())
        except (json.JSONDecodeError, TypeError):
            continue
        for item in json_values(data):
            item_type = item.get("@type")
            if item_type == "Product" or (
                isinstance(item_type, list) and "Product" in item_type
            ):
                return item
    return {}


def first_text(soup: BeautifulSoup, selectors: tuple[str, ...]) -> str:
    for selector in selectors:
        element = soup.select_one(selector)
        if element:
            value = clean(str(element.get("content", "") or element.get_text(" ")))
            if value:
                return value
    return ""


def product_name(soup: BeautifulSoup, data: dict[str, Any]) -> str:
    return clean(str(data.get("name", ""))) or first_text(
        soup,
        (
            'meta[property="og:title"]',
            "h1",
            'meta[name="title"]',
            "title",
        ),
    )


def product_price(soup: BeautifulSoup, data: dict[str, Any]) -> str:
    offers = data.get("offers", {})
    if isinstance(offers, list):
        offers = offers[0] if offers else {}
    if isinstance(offers, dict) and offers.get("price") is not None:
        return clean(str(offers["price"]))

    value = first_text(
        soup,
        (
            'meta[itemprop="price"]',
            'meta[property="product:price:amount"]',
            '[itemprop="price"]',
            "[data-price]",
        ),
    )
    if value:
        return value

    price_pattern = re.compile(r"(?:€|EUR)\s?\d+[,.]\d{2}")
    for element in soup.select('[class*="price"], [id*="price"]'):
        match = price_pattern.search(clean(element.get_text(" ")))
        if match:
            return match.group(0)
    return ""


def add_pair(pairs: dict[str, str], label: str, value: str) -> None:
    label = clean(label).casefold().rstrip(":")
    value = clean(value)
    if label and value and label not in pairs:
        pairs[label] = value


def specification_pairs(soup: BeautifulSoup) -> dict[str, str]:
    pairs: dict[str, str] = {}

    for row in soup.select('[data-testid="product-specifications-item"]'):
        columns = row.select("div")
        if len(columns) >= 2:
            add_pair(
                pairs,
                columns[0].get_text(" "),
                columns[1].get_text(" "),
            )

    return pairs


def parse_product(html: str, url: str) -> list[str]:
    soup = BeautifulSoup(html, "lxml")
    data = product_json(soup)
    pairs = specification_pairs(soup)
    values = [url, product_name(soup, data), product_price(soup, data)]
    values.extend(pairs.get(parameter.casefold(), "") for parameter in PARAMETERS)
    return [clean(value) for value in values]


def main() -> None:
    processed = 0
    scraped = 0
    for line in sys.stdin:
        url = line.strip()
        if not url:
            continue
        processed += 1
        logger.info(f"Product {processed}: {url}")
        try:
            row = parse_product(fetch(url), url)
            scraped += 1
        except Exception as error:  # noqa: BLE001 - one bad page must not stop the run
            # Keep one row per input URL even when the page cannot be scraped.
            logger.error("Could not scrape %s: %s", url, error)
            row = [url] + [""] * (2 + len(PARAMETERS))
        print("\t".join(row), flush=True)
    logger.info(f"Scraped {scraped} of {processed} products")


if __name__ == "__main__":
    main()
