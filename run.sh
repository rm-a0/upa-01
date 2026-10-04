#!/bin/sh
# Collect product URLs into url_test.txt, then scrape the first 10 of them to stdout.
set -eu

cd "$(dirname "$0")"

PY=.venv/bin/python
URLS_SCRIPT=get_urls.py
SCRAPER_SCRIPT=scraper.py
URLS_FILE=url_test.txt

if [ ! -x "$PY" ]; then
    echo "Virtual environment not found, run ./build.sh first." >&2
    exit 1
fi

"$PY" "$URLS_SCRIPT" > "$URLS_FILE"
head -n 10 "$URLS_FILE" | "$PY" "$SCRAPER_SCRIPT"
