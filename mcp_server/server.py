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
    """Find foods in the USDA FoodData Central database by free-text name. Use this FIRST when the user mentions a food by name and you need its `fdc_id` for any of the other nutrition_* tools. Returns ranked matches with fdc_id, description, brand_owner, and a quick macro summary (calories/protein/carbs/fat per 100g). Charges $0.001 USDC per call.

    Args:
        q: Free-text food name (e.g. "banana", "greek yogurt", "chicken breast").
        limit: Max results to return, 1-50. Default 10. Use a small limit unless you need to browse.
    """
    r = await _client().get("/v1/nutrition/search", params={"q": q, "limit": limit})
    r.raise_for_status()
    return r.json()


@mcp.tool()
async def nutrition_detail(fdc_id: int) -> dict[str, Any]:
    """Get the full per-100g nutrition profile for one specific food. Use this when you have an `fdc_id` (from nutrition_search) and the user needs micronutrients beyond just calories/protein/carbs/fat. Returns all 13 tracked nutrients: calories, protein, fat, carbs, fiber, sugar, sodium, cholesterol, saturated_fat, vitamin_c, calcium, iron, potassium. Missing nutrients are `null`, not 0. Charges $0.002 USDC per call.

    Args:
        fdc_id: USDA FoodData Central ID, obtained from nutrition_search.
    """
    r = await _client().get(f"/v1/nutrition/detail/{fdc_id}")
    r.raise_for_status()
    return r.json()


@mcp.tool()
async def nutrition_compare(fdc_ids: list[int]) -> dict[str, Any]:
    """Compare 2 to 5 foods side by side. Use this when the user asks "which is healthier," "which has more protein," or any cross-food comparison — it's cheaper and clearer than calling nutrition_detail multiple times. Returns each food's full nutrition plus per-nutrient winners (highest protein, lowest sodium, etc.). Charges $0.003 USDC per call.

    Args:
        fdc_ids: 2 to 5 USDA FDC IDs to compare.
    """
    r = await _client().post("/v1/nutrition/compare", json={"fdc_ids": fdc_ids})
    r.raise_for_status()
    return r.json()


@mcp.tool()
async def nutrition_recipe(ingredients: list[dict[str, Any]]) -> dict[str, Any]:
    """Sum nutrition across a recipe of weighted ingredients. Use this for meal planning, recipe analysis, or any "what are the totals if I combine X grams of A with Y grams of B" task. Each food's per-100g nutrition is scaled by grams/100 then summed. Charges $0.005 USDC per call.

    Args:
        ingredients: List of {"fdc_id": int, "grams": float} pairs. At least one; weights in grams.
    """
    r = await _client().post("/v1/nutrition/recipe", json={"ingredients": ingredients})
    r.raise_for_status()
    return r.json()


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
