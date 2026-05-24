"""Claude agent that plans a day of meals using NutriRef.

Usage:
    pip install anthropic httpx eth-account x402
    export ANTHROPIC_API_KEY=sk-ant-...
    export PAYER_PRIVATE_KEY=0x...funded-base-mainnet-wallet-key...
    python plan_meal.py "2000 calories, at least 120g protein, vegetarian"

Each tool call charges a small amount of USDC ($0.001–$0.005) to the payer
wallet on Base mainnet. A planning session typically costs $0.02–$0.10.
"""

import asyncio
import json
import os
import sys

import httpx
from anthropic import AsyncAnthropic
from eth_account import Account
from x402.client import x402Client
from x402.http.clients.httpx import wrapHttpxWithPayment
from x402.mechanisms.evm.exact import register_exact_evm_client


NUTRIREF_BASE_URL = os.environ.get("NUTRIREF_BASE_URL", "https://nutriref.xyz")
MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-6")


# Tool definitions Claude sees. Exact JSON schemas match NutriRef's endpoints.
TOOLS = [
    {
        "name": "nutrition_search",
        "description": (
            "Find foods in the USDA FoodData Central database by free-text name. "
            "Use FIRST when the user mentions a food and you need its fdc_id. "
            "Returns ranked matches with fdc_id, description, brand_owner, and "
            "macros. Costs $0.001 USDC."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "q": {"type": "string", "description": "Food name to search."},
                "limit": {"type": "integer", "minimum": 1, "maximum": 50, "default": 10},
            },
            "required": ["q"],
        },
    },
    {
        "name": "nutrition_detail",
        "description": (
            "Full per-100g nutrition (13 nutrients) for one food by fdc_id. "
            "Use when you need micronutrients beyond the macros from search. "
            "Costs $0.002 USDC."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"fdc_id": {"type": "integer"}},
            "required": ["fdc_id"],
        },
    },
    {
        "name": "nutrition_compare",
        "description": (
            "Compare 2–5 foods side by side; returns each food's nutrition plus "
            "per-nutrient winners. Use for cross-food choices ('which has more "
            "protein?'). Costs $0.003 USDC."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "fdc_ids": {"type": "array", "items": {"type": "integer"}, "minItems": 2, "maxItems": 5}
            },
            "required": ["fdc_ids"],
        },
    },
    {
        "name": "nutrition_recipe",
        "description": (
            "Scale each ingredient's per-100g nutrition by grams/100 and sum across "
            "all ingredients. Use to validate the totals of a planned meal. Costs "
            "$0.005 USDC."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "ingredients": {
                    "type": "array",
                    "minItems": 1,
                    "items": {
                        "type": "object",
                        "properties": {
                            "fdc_id": {"type": "integer"},
                            "grams": {"type": "number", "exclusiveMinimum": 0},
                        },
                        "required": ["fdc_id", "grams"],
                    },
                }
            },
            "required": ["ingredients"],
        },
    },
]


def _build_x402_client() -> x402Client:
    key = os.environ.get("PAYER_PRIVATE_KEY")
    if not key:
        sys.exit("Set PAYER_PRIVATE_KEY (a Base mainnet wallet's private key with USDC).")
    account = Account.from_key(key)
    client = x402Client()
    register_exact_evm_client(client, account)
    return client


async def _call_tool(http: httpx.AsyncClient, name: str, args: dict) -> dict:
    if name == "nutrition_search":
        r = await http.get("/v1/nutrition/search", params=args)
    elif name == "nutrition_detail":
        r = await http.get(f"/v1/nutrition/detail/{args['fdc_id']}")
    elif name == "nutrition_compare":
        r = await http.post("/v1/nutrition/compare", json=args)
    elif name == "nutrition_recipe":
        r = await http.post("/v1/nutrition/recipe", json=args)
    else:
        return {"error": f"unknown tool: {name}"}
    r.raise_for_status()
    return r.json()


async def main() -> None:
    goal = " ".join(sys.argv[1:]) or "2000 calories, at least 120g protein, balanced"
    print(f"Goal: {goal}\n")

    anthropic = AsyncAnthropic()
    x402 = _build_x402_client()

    system = (
        "You plan healthy daily meal plans by consulting real USDA nutrition data "
        "via the nutrition_* tools. Strategy: use nutrition_search to discover "
        "fdc_ids for candidate foods, then nutrition_recipe to validate the "
        "actual totals of each meal you compose. Aim for whole foods. Report the "
        "final plan concisely as a list of meals with ingredients (with grams) "
        "and totals."
    )

    messages: list[dict] = [
        {"role": "user", "content": f"Plan a day of meals (breakfast, lunch, dinner) meeting this goal: {goal}"}
    ]

    async with wrapHttpxWithPayment(x402, base_url=NUTRIREF_BASE_URL, timeout=30.0) as http:
        for _ in range(15):  # bounded loop guard
            resp = await anthropic.messages.create(
                model=MODEL,
                max_tokens=1500,
                system=system,
                tools=TOOLS,
                messages=messages,
            )

            if resp.stop_reason == "end_turn":
                text = "\n".join(b.text for b in resp.content if getattr(b, "type", None) == "text")
                print("\n=== plan ===\n" + text)
                return

            # Tool-use turn: record assistant message, run tools, return results.
            messages.append({"role": "assistant", "content": resp.content})
            tool_results = []
            for block in resp.content:
                if getattr(block, "type", None) != "tool_use":
                    continue
                print(f"  → {block.name}({json.dumps(block.input)})")
                try:
                    result = await _call_tool(http, block.name, dict(block.input))
                    payload = json.dumps(result)[:4000]
                except Exception as exc:
                    payload = json.dumps({"error": str(exc)})
                tool_results.append({"type": "tool_result", "tool_use_id": block.id, "content": payload})
            messages.append({"role": "user", "content": tool_results})

        print("(hit turn limit without an end_turn)")


if __name__ == "__main__":
    asyncio.run(main())
