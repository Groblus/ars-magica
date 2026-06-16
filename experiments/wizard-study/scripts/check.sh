#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

python3 -m compileall -q generation tests
PYTHONPATH=. python3 -m unittest discover -s tests
npm --prefix web run build
