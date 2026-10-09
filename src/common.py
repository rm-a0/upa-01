import logging
import sys
import time

import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry

BASE_URL = "https://www.knivesandtools.com"
REQUEST_DELAY = 2.0
DEFAULT_TIMEOUT = 20

_session = requests.Session()
_session.headers["User-Agent"] = "..."
_retry = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET", "HEAD"],
)
_session.mount("https://", HTTPAdapter(max_retries=_retry))

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] [%(name)s] %(message)s [%(asctime)s]",
    datefmt="%H:%M:%S",
    stream=sys.stderr,
)
log = logging.getLogger()


def fetch(url: str) -> str:
    """Sleep, GET the url, raise on HTTP error, return the HTML text."""
    time.sleep(REQUEST_DELAY)
    response = _session.get(url=url, timeout=DEFAULT_TIMEOUT)
    response.raise_for_status()
    return response.text
