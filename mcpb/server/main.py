"""MCPB entry point for the NutriRef MCP server.

`uv run --directory <bundle> server/main.py` resolves deps from the bundle's
pyproject.toml and runs this. The bundled `mcp_server` package sits next to
this file so it imports as a sibling.
"""

from mcp_server.server import main

if __name__ == "__main__":
    main()
