# NutriRef

[![NutriRef MCP server](https://glama.ai/mcp/servers/Younghef/nutriref-api/badges/score.svg)](https://glama.ai/mcp/servers/Younghef/nutriref-api)

**Pay-per-call USDA nutrition data for AI agents.** Structured FoodData Central via the [x402](https://www.x402.org/) micropayment protocol — agents pay $0.001–$0.005 in USDC per request, no signup, no API keys, no human auth flows.

Live at **<https://nutriref.xyz>**. Spec at [/openapi.json](https://nutriref.xyz/openapi.json) · Swagger at [/docs](https://nutriref.xyz/docs) · Bazaar discovery at [/.well-known/x402](https://nutriref.xyz/.well-known/x402).

## Endpoints

| Method | Path | Price | Cache |
|---|---|---|---|
| `GET`  | `/v1/nutrition/search?q=&limit=` | $0.001 | 24h |
| `GET`  | `/v1/nutrition/detail/{fdc_id}` | $0.002 | 7d |
| `POST` | `/v1/nutrition/compare` | $0.003 | derived |
| `POST` | `/v1/nutrition/recipe` | $0.005 | derived |

All values per 100g. Missing nutrients are `null`, not `0`. `compare` returns per-nutrient winners (highest protein, lowest sodium, etc.). `recipe` scales by grams and sums.

## Use it from Claude (or any MCP agent)

NutriRef ships an MCP server that exposes the four endpoints as native tools. Install once:

```bash
git clone https://github.com/Younghef/nutriref-api.git
cd nutriref-api
pip install -e ".[mcp]"
```

> A PyPI release is planned. Until then the source install above is the supported path.

Then add this to your MCP client config (Claude Desktop's `claude_desktop_config.json`, Claude Code's MCP settings, etc.):

```json
{
  "mcpServers": {
    "nutriref": {
      "command": "python",
      "args": ["-m", "mcp_server"],
      "env": {
        "PAYER_PRIVATE_KEY": "0x...your-funded-wallet-key...",
        "NUTRIREF_BASE_URL": "https://nutriref.xyz"
      }
    }
  }
}
```

The wallet needs USDC on Base mainnet — gas is sponsored by the facilitator, so you only need stablecoin balance. The agent now has `nutrition_search`, `nutrition_detail`, `nutrition_compare`, `nutrition_recipe` and auto-pays per call.

## Use it from any HTTP client

Unpaid requests get `402 Payment Required` with x402 payment instructions. Any x402-aware client signs a gasless USDC authorization (EIP-3009) and retries automatically:

```python
import asyncio
from eth_account import Account
from x402.client import x402Client
from x402.http.clients.httpx import wrapHttpxWithPayment
from x402.mechanisms.evm.exact import register_exact_evm_client

account = Account.from_key("0x...funded-wallet-key...")
client = x402Client(); register_exact_evm_client(client, account)

async def main():
    async with wrapHttpxWithPayment(client, base_url="https://nutriref.xyz") as http:
        r = await http.get("/v1/nutrition/detail/2012128")
        print(r.json())

asyncio.run(main())
```

## Response example

`GET /v1/nutrition/detail/173944`:

```json
{
  "fdc_id": 173944,
  "description": "Banana, raw",
  "data_type": "Foundation",
  "serving_size": 100, "serving_size_unit": "g",
  "calories": 89.0,  "protein": 1.1,    "fat": 0.3,
  "carbs": 22.8,     "fiber": 2.6,      "sugar": 12.2,
  "sodium": 1.0,     "cholesterol": null, "saturated_fat": 0.1,
  "vitamin_c": 8.7,  "calcium": 5.0,    "iron": 0.3,  "potassium": 358.0
}
```

---

## Self-hosting

NutriRef is open source; the live instance at `nutriref.xyz` is one deployment among many possible. To run your own:

```bash
cp .env.example .env
# fill in USDA_API_KEY (free at https://fdc.nal.usda.gov/api-key-signup.html)
# and X402_RECEIVER_ADDRESS (an EVM address that should receive payments)
docker compose up --build
curl http://localhost:8000/health
```

### Configuration

| Var | Required | Default | Purpose |
|---|---|---|---|
| `USDA_API_KEY` | yes | — | Free key from [fdc.nal.usda.gov](https://fdc.nal.usda.gov/api-key-signup.html) |
| `USDA_BASE_URL` | no | `https://api.nal.usda.gov/fdc/v1` | |
| `REDIS_URL` | no | `redis://redis:6379/0` | Response cache |
| `X402_NETWORK` | no | `base-sepolia` | `base` for mainnet |
| `X402_RECEIVER_ADDRESS` | yes | — | EVM address that receives USDC |
| `X402_FACILITATOR_URL` | no | `https://x402.org/facilitator` | `https://api.cdp.coinbase.com` for mainnet |
| `CDP_API_KEY_ID` | mainnet only | — | Coinbase Developer Platform key ID |
| `CDP_API_KEY_SECRET` | mainnet only | — | Coinbase Developer Platform key secret |
| `LOG_LEVEL` | no | `INFO` | |

For mainnet you need a Coinbase CDP account and the public x402 facilitator at `https://api.cdp.coinbase.com`. Testnet works for free with the community facilitator at `https://x402.org/facilitator`.

### Architecture

```
agent → x402 middleware → route handler → cache (Redis) → USDA FDC API
```

`search` and `detail` cache USDA responses directly. `compare` and `recipe` compose from the cached `detail` data — no extra USDA calls when warm. The cache is a meaningful cost lever: warm requests return in <50ms and never hit USDA.

### Tests

```bash
pip install -e ".[dev]"
pytest
```

## Example: Claude agent that uses NutriRef

`examples/meal-planner/` is a complete, ~150-line agent that gives Claude
the four NutriRef endpoints as tools and asks it to plan a day of meals
hitting a calorie/protein goal. Worth reading if you're wiring NutriRef
into your own agent — the tool schemas and the payment loop are all
there. See `examples/meal-planner/README.md`.

## Repo layout

```
app/                # FastAPI service
  main.py             # app factory + x402 init
  routes/             # search, detail, compare, recipe
  landing.py          # / (public landing page)
  discovery.py        # /.well-known/x402, /llms.txt, /.well-known/ai-plugin.json, /logo.svg
  usda.py             # async USDA client
  cache.py            # Redis wrapper
  normalize.py        # USDA → flat 13-nutrient schema
mcp_server/         # MCP server wrapper for agent use
examples/           # worked agent examples (meal planner)
scripts/            # CDP wallet bootstrap + payer-side test
tests/              # pytest + respx + fakeredis
```

## Acknowledgments

- [USDA FoodData Central](https://fdc.nal.usda.gov/) for the data.
- [x402](https://www.x402.org/) for the payment protocol.
- [`fastapi-x402`](https://pypi.org/project/fastapi-x402/) for the server middleware (with a small EIP-712 patch we apply at startup for Base mainnet USDC).
