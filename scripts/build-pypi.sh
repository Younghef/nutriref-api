#!/usr/bin/env bash
# Build the nutriref-mcp PyPI distribution (sdist + wheel) from current source.
#
# Output: pypi/dist/
#
# Publish with:
#   python -m twine upload pypi/dist/*
set -euo pipefail
cd "$(dirname "$0")/.."

echo "→ syncing mcp_server/ into pypi/ from canonical mcp_server/"
rm -rf pypi/mcp_server pypi/dist pypi/build pypi/*.egg-info
cp -r mcp_server pypi/mcp_server
find pypi/mcp_server -name '__pycache__' -type d -exec rm -rf {} +

cd pypi
echo "→ building sdist + wheel"
PY="$(command -v python || command -v python3 || command -v py || true)"
if [ -z "$PY" ]; then
  echo "error: no python interpreter found on PATH" >&2
  exit 1
fi
"$PY" -m build

echo "✓ built:"
ls -1 dist
