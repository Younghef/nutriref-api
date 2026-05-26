#!/usr/bin/env bash
# Rebuild the NutriRef MCPB bundle from current source.
#
# Output: build/nutriref.mcpb
#
# After this completes, publish to Smithery with:
#   npx @smithery/cli login           # one-time, opens a browser
#   npx @smithery/cli mcp publish ./build/nutriref.mcpb -n derekhefley/nutriref

set -euo pipefail
cd "$(dirname "$0")/.."

echo "→ refreshing mcpb/server/mcp_server/ from canonical mcp_server/"
rm -rf mcpb/server/mcp_server
cp -r mcp_server mcpb/server/mcp_server
find mcpb/server -name '__pycache__' -type d -exec rm -rf {} +

mkdir -p build
echo "→ validating manifest"
npx --yes @anthropic-ai/mcpb validate mcpb/manifest.json

echo "→ packing"
npx --yes @anthropic-ai/mcpb pack mcpb build/nutriref.mcpb

echo "✓ built: build/nutriref.mcpb"

# Emit SHA-256 for the official MCP registry's server.json (fileSha256).
if command -v sha256sum >/dev/null 2>&1; then
  SHA=$(sha256sum build/nutriref.mcpb | awk '{print $1}')
elif command -v shasum >/dev/null 2>&1; then
  SHA=$(shasum -a 256 build/nutriref.mcpb | awk '{print $1}')
else
  SHA=""
fi
if [ -n "$SHA" ]; then
  echo "  sha256: $SHA"
  echo "  → paste into server.json packages[0].fileSha256 before mcp-publisher publish"
fi
