"""FastMCP server exposing NutriRef as four tools.

Each tool call makes a real x402 micropayment against NUTRIREF_BASE_URL using
PAYER_PRIVATE_KEY. The agent operator funds that wallet with USDC on Base.
"""

import os
from typing import Any

import httpx
from eth_account import Account
from mcp.server.fastmcp import FastMCP
from x402.client import x402Client
from x402.http.clients.httpx import wrapHttpxWithPayment
from x402.mechanisms.evm.exact import register_exact_evm_client


NUTRIREF_BASE_URL = os.environ.get("NUTRIREF_BASE_URL", "https://nutriref.xyz")

_http: httpx.AsyncClient | None = None


def _client() -> httpx.AsyncClient:
    global _http
    if _http is not None:
        return _http
    key = os.environ.get("PAYER_PRIVATE_KEY")
    if not key:
        raise RuntimeError(
            "PAYER_PRIVATE_KEY env var is required to make a paid NutriRef call. "
            "Set it to a Base mainnet wallet private key with USDC balance "
            "(each call costs $0.001-$0.005)."
        )
    account = Account.from_key(key)
    x402 = x402Client()
    register_exact_evm_client(x402, account)
    _http = wrapHttpxWithPayment(x402, base_url=NUTRIREF_BASE_URL, timeout=30.0)
    return _http


def _hint_for(status: int, code: str | None) -> str:
    if status == 402:
        return "Payment was required but the x402 flow did not complete — verify PAYER_PRIVATE_KEY's wallet has USDC on Base and the facilitator is reachable."
    if status == 404:
        return "The fdc_id was not found in USDA FoodData Central. Re-check it with nutrition_search."
    if status == 503 and code == "cache_unavailable":
        return "NutriRef's cache backend is down — retry in a few seconds; if it persists, the operator should check REDIS_URL."
    if status >= 500:
        return "Upstream error on the NutriRef side. Retry; if it persists, the operator should check server logs."
    if status == 429:
        return "Rate-limited upstream — wait a few seconds and retry."
    return "Inspect status and message; this is the raw upstream payload."


async def _request(method: str, path: str, **kw: Any) -> dict[str, Any]:
    """Single source of truth for HTTP→tool-result conversion.

    Catches httpx errors (including non-2xx responses) and returns a structured
    {status, error, message, hint} dict instead of letting an HTTPStatusError
    bubble into the MCP tool boundary as an unstructured stack trace.
    """
    try:
        r = await getattr(_client(), method)(path, **kw)
    except httpx.RequestError as e:
        return {
            "status": 0,
            "error": "transport_error",
            "message": f"{e.__class__.__name__}: {e}",
            "hint": "Could not reach NutriRef. Check network and NUTRIREF_BASE_URL.",
        }
    if r.is_success:
        return r.json()
    body: dict[str, Any] = {}
    try:
        body = r.json() if r.content else {}
    except ValueError:
        body = {"raw": r.text[:500]}
    code = body.get("error") if isinstance(body.get("error"), str) else None
    return {
        "status": r.status_code,
        "error": code or f"http_{r.status_code}",
        "message": body.get("message") or body.get("error") or r.text[:500],
        "hint": _hint_for(r.status_code, code),
    }


mcp = FastMCP(
    "nutriref",
    instructions=(
        "NutriRef: structured USDA FoodData Central nutrition data. Each call charges "
        "USDC from the configured PAYER_PRIVATE_KEY wallet on Base mainnet via x402. "
        "Use nutrition_search first to get an fdc_id, then nutrition_detail for the "
        "full breakdown. nutrition_compare and nutrition_recipe compose from cached "
        "detail data."
    ),
)


@mcp.tool()
async def nutrition_search(q: str, limit: int = 10) -> dict[str, Any]:
    """Find foods in the USDA FoodData Central database by free-text name. Use this FIRST when the user mentions a food by name and you need its `fdc_id` for any of the other nutrition_* tools. Returns ranked matches with fdc_id, description, brand_owner, and a quick macro summary (calories/protein/carbs/fat per 100g). Charges $0.001 USDC per call.

    Args:
        q: Free-text food name (e.g. "banana", "greek yogurt", "chicken breast").
        limit: Max results to return, 1-50. Default 10. Use a small limit unless you need to browse.
    """
    return await _request("get", "/v1/nutrition/search", params={"q": q, "limit": limit})


@mcp.tool()
async def nutrition_detail(fdc_id: int) -> dict[str, Any]:
    """Get the full per-100g nutrition profile for one specific food. Use this when you have an `fdc_id` (from nutrition_search) and the user needs micronutrients beyond just calories/protein/carbs/fat. Returns all 13 tracked nutrients: calories, protein, fat, carbs, fiber, sugar, sodium, cholesterol, saturated_fat, vitamin_c, calcium, iron, potassium. Missing nutrients are `null`, not 0. Charges $0.002 USDC per call.

    Args:
        fdc_id: USDA FoodData Central ID, obtained from nutrition_search.
    """
    return await _request("get", f"/v1/nutrition/detail/{fdc_id}")


@mcp.tool()
async def nutrition_compare(fdc_ids: list[int]) -> dict[str, Any]:
    """Compare 2 to 5 foods side by side. Use this when the user asks "which is healthier," "which has more protein," or any cross-food comparison — it's cheaper and clearer than calling nutrition_detail multiple times. Returns each food's full nutrition plus per-nutrient winners (highest protein, lowest sodium, etc.). Charges $0.003 USDC per call.

    Args:
        fdc_ids: 2 to 5 USDA FDC IDs to compare.
    """
    return await _request("post", "/v1/nutrition/compare", json={"fdc_ids": fdc_ids})


@mcp.tool()
async def nutrition_recipe(ingredients: list[dict[str, Any]]) -> dict[str, Any]:
    """Sum nutrition across a recipe of weighted ingredients. Use this for meal planning, recipe analysis, or any "what are the totals if I combine X grams of A with Y grams of B" task. Each food's per-100g nutrition is scaled by grams/100 then summed. Charges $0.005 USDC per call.

    Args:
        ingredients: List of {"fdc_id": int, "grams": float} pairs. At least one; weights in grams.
    """
    return await _request("post", "/v1/nutrition/recipe", json={"ingredients": ingredients})


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
