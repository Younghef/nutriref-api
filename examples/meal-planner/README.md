# Meal planner — Claude + NutriRef agent example

A small, complete example of an LLM agent using NutriRef. Claude is given a
nutrition goal ("1800 calories, ≥120g protein, vegetarian") and the four
NutriRef endpoints as tools. It plans a day of meals end-to-end:

- searches the USDA database to find candidate foods,
- pulls full nutrition for the contenders,
- assembles meals and validates totals against the recipe endpoint,
- returns a final plan.

This doubles as a reference for anyone wiring NutriRef into their own
agent — the tool definitions, the request/response shapes, and the
payment flow are all here.

## Setup

```bash
pip install anthropic httpx eth-account x402
export ANTHROPIC_API_KEY=sk-ant-...
export PAYER_PRIVATE_KEY=0x...funded-base-mainnet-wallet-key...
# optional: override the target
export NUTRIREF_BASE_URL=https://nutriref.xyz
```

The payer wallet must hold real USDC on Base mainnet. A typical run makes
10–20 tool calls and costs **$0.02–$0.10 in USDC**, plus your Anthropic
API usage.

## Run

```bash
python plan_meal.py "2000 calories, at least 120g protein, vegetarian"
```

Output shows each tool call as Claude makes it, followed by the final plan.

## What it demonstrates

- **Defining NutriRef endpoints as Claude tools** — exact JSON schemas you
  can copy into any tool-using agent built on the Anthropic SDK.
- **The x402 payment loop is invisible to the agent.** `wrapHttpxWithPayment`
  intercepts 402 responses, signs a USDC authorization, retries — Claude
  just sees 200s with nutrition data.
- **Composing multiple endpoints in one workflow** — search → detail/compare
  → recipe — exactly the chain NutriRef is designed for.

## Files

- `plan_meal.py` — the agent. ~150 lines, async, single file.
- This README.
