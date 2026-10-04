#!/bin/sh
# Create a local virtual environment and install dependencies into it.
set -eu

cd "$(dirname "$0")"

PYTHON="${PYTHON:-python3}"

"$PYTHON" -m venv .venv
.venv/bin/pip install --quiet --upgrade pip
.venv/bin/pip install --quiet -r requirements.txt

echo "Build OK: $(.venv/bin/python --version)" >&2
