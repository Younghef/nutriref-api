"""End-to-end stdio test of the NutriRef MCP server.

Spawns the server as `python -m mcp_server`, speaks the MCP protocol over
stdio, lists tools, and calls `nutrition_search`. Costs $0.001 USDC per
run (one search call).

Usage:
    pip install -e ".[mcp]"
    # PAYER_PRIVATE_KEY must be set in .env to a funded Base mainnet wallet
    python scripts/test_mcp_stdio.py
"""

import asyncio
import json
import os
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


def _load_env() -> None:
    for line in (Path(__file__).resolve().parent.parent / ".env").read_text(encoding="utf-8").splitlines():
        if line.startswith("PAYER_PRIVATE_KEY="):
            os.environ["PAYER_PRIVATE_KEY"] = line.split("=", 1)[1].strip()
            return
    sys.exit("PAYER_PRIVATE_KEY not found in .env")


async def main() -> None:
    _load_env()
    os.environ["NUTRIREF_BASE_URL"] = os.environ.get("NUTRIREF_BASE_URL", "https://nutriref.xyz")

    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "mcp_server"],
        env=os.environ.copy(),
    )

    print(f"-> spawning: {sys.executable} -m mcp_server")
    print(f"-> target:   {os.environ['NUTRIREF_BASE_URL']}")
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            init = await session.initialize()
            print(f"\n[initialize] server={init.serverInfo.name} v{init.serverInfo.version}")

            tools = await session.list_tools()
            print(f"\n[tools/list] {len(tools.tools)} tools")
            for t in tools.tools:
                print(f"  - {t.name}: {(t.description or '')[:70].strip()}...")

            print(f"\n[tools/call] nutrition_search(q='apple', limit=2)")
            result = await session.call_tool("nutrition_search", {"q": "apple", "limit": 2})
            text = result.content[0].text if result.content else ""
            try:
                data = json.loads(text)
                print(f"  count: {data.get('count')}")
                for hit in data.get("results", [])[:2]:
                    print(f"  - fdc_id={hit['fdc_id']} desc={hit['description']!r} cal={hit['calories']}")
            except json.JSONDecodeError:
                print(f"  (raw, first 300 chars): {text[:300]}")

            print("\n[OK] MCP server stdio test passed")


if __name__ == "__main__":
    asyncio.run(main())
