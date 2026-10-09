import logging
from common import BASE_URL, fetch
from bs4 import BeautifulSoup
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

CATEGORY_URL = BASE_URL + "/en/ct/flashlights.htm"
LIMIT = 200


def page_url(page: int) -> str:
    return f"{CATEGORY_URL}?p={page}"


def parse_listing(html: str) -> list[str]:
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

    logger.info(f"Fetched {len(seen)} urls.")
    for url in list(seen)[:LIMIT]:
        print(url)


if __name__ == "__main__":
    main()
