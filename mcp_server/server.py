"""FastMCP server exposing NutriRef as four tools.

Each tool call makes a real x402 micropayment against NUTRIREF_BASE_URL using
PAYER_PRIVATE_KEY. The agent operator funds that wallet with USDC on Base.
"""

import os
import sys
from typing import Any

import httpx
from eth_account import Account
from mcp.server.fastmcp import FastMCP
from x402.client import x402Client
from x402.http.clients.httpx import wrapHttpxWithPayment
from x402.mechanisms.evm.exact import register_exact_evm_client


PAYER_PRIVATE_KEY = os.environ.get("PAYER_PRIVATE_KEY")
NUTRIREF_BASE_URL = os.environ.get("NUTRIREF_BASE_URL", "https://nutriref.xyz")

if not PAYER_PRIVATE_KEY:
    sys.exit(
        "PAYER_PRIVATE_KEY env var is required. Provide a Base mainnet wallet "
        "private key with USDC balance — each NutriRef call costs $0.001-$0.005."
    )

_account = Account.from_key(PAYER_PRIVATE_KEY)
_x402 = x402Client()
register_exact_evm_client(_x402, _account)
_http: httpx.AsyncClient | None = None


def _client() -> httpx.AsyncClient:
    global _http
    if _http is None:
        _http = wrapHttpxWithPayment(_x402, base_url=NUTRIREF_BASE_URL, timeout=30.0)
    return _http


mcp = FastMCP(
    "nutriref",
    instructions=(
        "NutriRef: structured USDA FoodData Central nutrition data. Each call charges "
        f"USDC from {_account.address} on Base mainnet via x402. Use nutrition_search "
        "first to get an fdc_id, then nutrition_detail for the full breakdown. "
        "nutrition_compare and nutrition_recipe compose from cached detail data."
    ),
)


@mcp.tool()
async def nutrition_search(q: str, limit: int = 10) -> dict[str, Any]:
    """Search USDA foods by name. Returns ranked matches with fdc_id and macros (calories, protein, carbs, fat). Costs $0.001 USDC.

    Args:
        q: Free-text food name to search (e.g. "banana", "greek yogurt").
        limit: Max results to return, 1-50. Default 10.
    """
    r = await _client().get("/v1/nutrition/search", params={"q": q, "limit": limit})
    r.raise_for_status()
    return r.json()


@mcp.tool()
async def nutrition_detail(fdc_id: int) -> dict[str, Any]:
    """Full nutrition for one food by USDA FDC ID. Returns all 13 tracked nutrients per 100g (missing values null, not 0). Costs $0.002 USDC.

    Args:
        fdc_id: USDA FoodData Central ID, from nutrition_search.
    """
    r = await _client().get(f"/v1/nutrition/detail/{fdc_id}")
    r.raise_for_status()
    return r.json()


@mcp.tool()
async def nutrition_compare(fdc_ids: list[int]) -> dict[str, Any]:
    """Compare 2-5 foods side by side. Returns each food's nutrition plus per-nutrient winners (highest protein, lowest sodium, etc.). Costs $0.003 USDC.

    Args:
        fdc_ids: 2 to 5 USDA FDC IDs to compare.
    """
    r = await _client().post("/v1/nutrition/compare", json={"fdc_ids": fdc_ids})
    r.raise_for_status()
    return r.json()


@mcp.tool()
async def nutrition_recipe(ingredients: list[dict[str, Any]]) -> dict[str, Any]:
    """Sum nutrition across a recipe of weighted ingredients. Scales each food's per-100g nutrition by grams/100 and sums. Costs $0.005 USDC.

    Args:
        ingredients: List of {"fdc_id": int, "grams": float} pairs (at least one).
    """
    r = await _client().post("/v1/nutrition/recipe", json={"ingredients": ingredients})
    r.raise_for_status()
    return r.json()


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
