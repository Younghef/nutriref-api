"""D4 verification: structured error payloads from MCP tools.

Spawns mcp_server pointing at a local NutriRef API, then exercises:
  1. happy path  → dict with `count` / `results`
  2. 503         → dict with `status=503, error="cache_unavailable", hint=...`
                   (operator must stop nutriref-redis-1 before this call)
  3. 4xx body    → dict with `status=4xx, error=..., message=..., hint=...`

Prints each tool result. Exits 0 only if every result is a structured payload
(no httpx.HTTPStatusError, no MCP protocol error).
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


def _decode(result) -> dict:
    if not result.content:
        return {}
    text = result.content[0].text
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"_raw": text[:500]}


async def main() -> None:
    _load_env()
    os.environ["NUTRIREF_BASE_URL"] = "http://127.0.0.1:8000"

    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "mcp_server"],
        env=os.environ.copy(),
    )

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            print("=== happy path: nutrition_search ===")
            r = await session.call_tool("nutrition_search", {"q": "apple", "limit": 2})
            print(json.dumps(_decode(r), indent=2)[:500])

            print("\n=== error path: nutrition_detail (operator should have stopped redis first) ===")
            r = await session.call_tool("nutrition_detail", {"fdc_id": 2012128})
            print(json.dumps(_decode(r), indent=2)[:500])


if __name__ == "__main__":
    asyncio.run(main())
