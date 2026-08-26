#!/usr/bin/env bash
set -euo pipefail

REPOSITORY_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$REPOSITORY_ROOT"

python -m pip install --requirement requirements-dev.txt
python -m playwright install chromium

printf '\nAuctions development container ready with Python %s.\n' "$(python --version | awk '{print $2}')"
