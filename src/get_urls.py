import logging
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from common import BASE_URL, fetch

logger = logging.getLogger(__name__)

CATEGORY_URL = BASE_URL + "/en/ct/flashlights.htm"
LIMIT = 200


def page_url(page: int) -> str:
    """Return the category listing url for the given page number."""
    return f"{CATEGORY_URL}?p={page}"


def parse_listing(html: str) -> list[str]:
    """Parse listing HTML, return unique absolute product urls in page order."""
    soup = BeautifulSoup(html, "lxml")
    if (slot := soup.select_one("#bottomslot")) is not None:
        slot.decompose()

    urls = []
    tags = soup.select('#listing a[href^="/en/pt/"]')
    for tag in tags:
        link = tag["href"]
        if link:
            urls.append(urljoin(BASE_URL, str(link)))

    return list(dict.fromkeys(urls))


def main() -> None:
    """Walk listing pages until LIMIT urls are collected, print them to stdout."""
    seen: dict[str, None] = {}
    page_number = 1
    while len(seen) < LIMIT:
        urls = parse_listing(fetch(page_url(page_number)))
        new = [u for u in urls if u not in seen]
        logger.info(f"Page {page_number}: {len(urls)} links")
        if not new:
            break
        seen.update(dict.fromkeys(new))
        page_number += 1

    logger.info(f"Fetched {len(seen)} urls")
    for url in list(seen)[:LIMIT]:
        print(url)


if __name__ == "__main__":
    main()
