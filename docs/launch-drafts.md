# NutriRef launch drafts

Copy-pasteable copy for each channel. **Review and edit before posting** — these are drafts, not autopilot. Pick the variants/tone that feels right for each audience.

A note on emojis: I've left them out so the drafts read clean. Add or remove to match the platform (Twitter tolerates more; CDP forum less; dev.to readable either way).

---

## 1. Twitter / X — launch tweet

Three variants, pick one. Replace the trailing `→` with whatever line break / preview you like; a single link at the end gives a clean OG card preview from `nutriref.xyz`.

### Variant A — terse builder

> Shipped: NutriRef.
>
> Pay-per-call USDA nutrition data for AI agents. No signup, no API keys. $0.001–$0.005 per request in USDC on Base via x402.
>
> Search, detail, compare, recipe. Plus an MCP server so any Claude/MCP agent plugs it in with one config block.
>
> https://nutriref.xyz

### Variant B — pitch-led

> Most APIs don't fit how agents actually work — signup forms, API keys, OAuth flows. So I built one that doesn't.
>
> NutriRef wraps USDA FoodData Central behind x402 micropayments. Agents pay USDC per request, no human in the loop.
>
> https://nutriref.xyz

### Variant C — show, don't tell

> An AI agent just paid me 0.002 USDC for a banana's macros.
>
> NutriRef is a pay-per-call USDA nutrition API for agents. Live on Base mainnet via x402. MCP server included.
>
> https://nutriref.xyz

### Reply thread (optional, if Variant A or B)

> Stack: FastAPI + fastapi-x402, Redis cache, Coinbase CDP as the mainnet facilitator, deployed on a $6 DO droplet. Caddy for HTTPS. The whole thing is open source.
>
> Honest gotchas in the build:
>
> - The public x402.org facilitator is testnet-only. Mainnet routes through Coinbase CDP, which means CDP API keys server-side.
>
> - fastapi-x402 advertises `"USDC"` as the EIP-712 token name on Base mainnet, but the contract's actual on-chain name is `"USD Coin"`. The payer signs against the wrong domain, the facilitator's `transferWithAuthorization` reverts, you get `invalid_payload`. One-line override in app code.
>
> Repo: <link to GitHub>

---

## 2. x402 Discord — `#showcase` / `#built-with-x402` style channel

> Hey all — built and launched NutriRef this week. It's a paid USDA FoodData Central API for AI agents, gated by x402.
>
> Live on Base mainnet at https://nutriref.xyz. Four endpoints: food search ($0.001), food detail ($0.002), side-by-side compare ($0.003), and recipe scale+sum ($0.005). All values normalized to a flat per-100g schema across 13 nutrients.
>
> Stack is fastapi-x402 + Redis + Coinbase CDP facilitator on mainnet, deployed via Docker Compose on a single DO droplet. Source: <link to GitHub>
>
> Two things worth flagging if anyone hits them:
>
> 1. fastapi-x402 0.1.6 hardcodes `eip712_name="USDC"` for `base` in its asset config, but the on-chain `name()` for `0x833589fCD6…` is `"USD Coin"`. The mismatch makes the facilitator's `transferWithAuthorization` revert with `invalid_payload`. Patched at startup with a 3-line `NETWORK_CONFIGS["base"].assets["usdc"].eip712_name = "USD Coin"` override. Avalanche Fuji is correct; only Base mainnet bites.
>
> 2. fastapi-x402 doesn't surface the in-band `extensions` field on its 402 challenges, so resources don't auto-catalog into the Bazaar via payment traffic. I shipped a parallel `/.well-known/x402` doc using the Bazaar discovery vocabulary in the meantime — open to discussing the right way to wire extensions through the FastAPI middleware.
>
> Happy to answer questions about the deploy or the consumer-side x402 client wiring.

---

## 3. Coinbase Developer Platform forum / Discord

> **Project showcase: NutriRef — USDA nutrition data for AI agents, monetized via x402 + CDP**
>
> Wanted to share a small project built on the CDP + x402 stack: NutriRef wraps the USDA FoodData Central API behind x402 micropayments so AI agents can pay per call in USDC on Base, with no signup or API-key flow.
>
> **Live:** https://nutriref.xyz (HTTPS, Base mainnet)
> **Source:** <link to GitHub>
> **Receiver wallet** is a CDP server account, provisioned via `cdp.evm.get_or_create_account` from the cdp-sdk. The mainnet facilitator at `https://api.cdp.coinbase.com` handles verify and settle; auth is the standard CDP JWT.
>
> Four endpoints, prices from $0.001 to $0.005. Each call returns normalized JSON (per-100g, 13 nutrient fields). Includes an MCP server wrapper so any Claude Desktop / Claude Code user can add NutriRef as native tools with one config block.
>
> **Implementation notes that might help others starting on this path:**
>
> - The receiver address is the only thing CDP gives you the public side of. Use `cdp.evm.get_or_create_account(name=...)` with a stable name so re-runs are idempotent. No wallet secret needed server-side beyond the CDP env vars.
>
> - For an agent-facing API, gasless settlement (the facilitator pays gas) is the killer feature — the consumer wallet only needs a USDC balance, no ETH.
>
> - One library issue worth flagging: `fastapi-x402` advertises `"USDC"` as the EIP-712 token name for Base mainnet, but the contract's on-chain `name()` is `"USD Coin"`. Mismatch makes signatures invalid and `transferWithAuthorization` reverts. I patch it at startup; happy to share the snippet if useful.
>
> Open to feedback on the API surface and any pointers on getting properly indexed in the Bazaar — currently I publish a parallel directory at `/.well-known/x402` since the upstream FastAPI middleware doesn't yet emit the in-band `extensions` field.

---

## 4. dev.to / Hashnode / Medium — long-form article

**Title options:**
- "I built an API that AI agents pay per call — no signup, no API keys"
- "Monetizing an API for AI agents with x402 and Coinbase CDP"
- "What it takes to put a real API behind x402 micropayments"

**Suggested tags:** `ai`, `agents`, `web3`, `python`, `fastapi`

---

### What changes when your customer is an AI agent

Most public APIs assume a human will sign up. They want an email, a password, a billing flow, sometimes a phone number. An autonomous agent can't do any of that. So the agent's developer signs up, gets a key, and hardcodes it. That works, but it means every new agent operator needs to negotiate access with every API provider, ahead of time.

[x402](https://www.x402.org/) is a protocol that flips this. The HTTP server returns `402 Payment Required` with payment instructions. An x402-aware client pays — in stablecoin, on-chain — and retries with proof. The server verifies the payment and serves the data. No accounts, no keys, no rate limiters: the wallet *is* the rate limiter.

I wanted to see what it actually takes to put a useful API behind this. The result is **NutriRef**: pay-per-call USDA nutrition data for AI agents. Live at [nutriref.xyz](https://nutriref.xyz). Source on GitHub: <link>.

### The product

Four endpoints, normalized JSON, per-100g values, 13 tracked nutrients:

| Endpoint | Price | What it returns |
|---|---|---|
| `GET /v1/nutrition/search?q=&limit=` | $0.001 | Ranked food matches with macros |
| `GET /v1/nutrition/detail/{fdc_id}` | $0.002 | Full normalized nutrition |
| `POST /v1/nutrition/compare` | $0.003 | Side-by-side with per-nutrient winners |
| `POST /v1/nutrition/recipe` | $0.005 | Scaled and summed across ingredients |

Search and detail proxy to USDA FoodData Central with Redis caching. Compare and recipe compose from the detail cache — when warm, they don't touch USDA at all.

### The stack

- **FastAPI** with the [`fastapi-x402`](https://pypi.org/project/fastapi-x402/) middleware for the payment gate
- **httpx (async)** for the USDA upstream
- **Redis** for response caching (24h for search, 7d for detail)
- **Pydantic v2** for request/response models
- **Docker Compose** — API + Redis as two services, deployed on a $6/mo DigitalOcean Droplet
- **Caddy** for automatic Let's Encrypt TLS
- **Coinbase CDP** as the receiver wallet provider and the mainnet x402 facilitator
- **MCP server wrapper** (using the official `mcp` Python SDK) so Claude / Claude Code can use NutriRef as native tools

### The implementation

Routes are stock FastAPI, with one decorator added per route:

```python
from fastapi_x402 import pay

@router.get("/detail/{fdc_id}", response_model=NormalizedFood)
@pay("$0.002")
async def detail(fdc_id: int) -> NormalizedFood:
    food = await get_detail_cached(fdc_id)
    return NormalizedFood(**food)
```

That's the whole gate. Anything without `X-PAYMENT` gets a 402 with x402 payment instructions; anything with a verified payment runs the handler.

A client sees this:

```python
async with wrapHttpxWithPayment(x402_client, base_url="https://nutriref.xyz") as http:
    r = await http.get("/v1/nutrition/detail/2012128")
    print(r.json())
```

`wrapHttpxWithPayment` is an httpx transport that catches 402s, signs the payment (gasless USDC, EIP-3009), and retries. The agent operator sees a normal 200.

### Going to mainnet — what surprised me

Testnet (Base Sepolia) works against the free public facilitator at `x402.org/facilitator`. Mainnet does not — Base mainnet (`eip155:8453`) isn't on its supported list. Mainnet routes through Coinbase's CDP facilitator at `https://api.cdp.coinbase.com`, which requires CDP API authentication (JWT). `fastapi-x402` handles this automatically if `CDP_API_KEY_ID` + `CDP_API_KEY_SECRET` are in the environment, but you need `cdp-sdk` installed for the JWT helper.

Then the actual mainnet bug: the first paid call against the deployed mainnet server returned 402 again with `invalid_payload`. The facilitator's diagnostic was clear once decoded — `transferWithAuthorization` had reverted. Root cause: `fastapi-x402` ships with `eip712_name="USDC"` for Base mainnet USDC in its asset config, but the contract's actual on-chain EIP-712 domain name is `"USD Coin"`. The payer signs an EIP-712 message against a domain that doesn't match the contract; the recovered signer is garbage; the contract rejects.

The fix is a three-line monkey-patch at startup:

```python
from fastapi_x402 import networks as x402_networks
_base_usdc = x402_networks.NETWORK_CONFIGS["base"].assets["usdc"]
_base_usdc.name = "USD Coin"
_base_usdc.eip712_name = "USD Coin"
```

Avalanche Fuji is correct in the same library, so it's a Base-specific oversight worth a PR upstream.

### The MCP wrapper

The most realistic adoption path for a small API right now is MCP. The agent operator adds one config block and gets four new tools:

```json
{
  "mcpServers": {
    "nutriref": {
      "command": "python", "args": ["-m", "mcp_server"],
      "env": {
        "PAYER_PRIVATE_KEY": "0x...funded-wallet-key...",
        "NUTRIREF_BASE_URL": "https://nutriref.xyz"
      }
    }
  }
}
```

The MCP server holds an x402 client keyed by `PAYER_PRIVATE_KEY` and forwards each tool call to the live API with payment. From the agent's perspective: `await nutrition_detail(fdc_id=2012128)` returns nutrition. Behind the scenes, a 402 happens, the wallet signs, USDC moves, the response arrives — all in one round trip from the agent's view.

### What I learned

1. **The pricing knob is interesting.** $0.001 per search call is cheap enough that an agent won't think twice, and yet it adds up if anyone actually uses the service. The wallet is also a per-agent rate limiter in a way that's much more aligned than a typical free-tier-then-pricing-page model.

2. **Gasless settlement is the unlock.** Asking agents to manage ETH for gas would be a non-starter; the EIP-3009 / facilitator pattern means a wallet only needs USDC.

3. **The directory side of the protocol matters.** An x402 API that exists but isn't discoverable might as well not exist. The Bazaar protocol (Coinbase's facilitator auto-catalogs resources from in-band 402 extensions) is the right primitive — it just needs the resource servers to start emitting the extensions field.

### Try it

- The API: `https://nutriref.xyz` (HTTPS, Base mainnet)
- The MCP server: `pip install ".[mcp]"` from the repo
- The source: <link to GitHub>

If you build something interesting against it, or you're working on adjacent x402 things, I'd love to hear about it. Reply here or find me at <your contact>.

---

## 5. Where else to post (in order of priority)

1. **Show HN** (Hacker News). One-shot — plan it. Title: `Show HN: NutriRef — pay-per-call USDA nutrition API for AI agents (x402, Base)`. Post 7-9am PT on a weekday for best chance of front page. Include a "What this is" comment immediately after submitting.
2. **r/ethdev** (Reddit) — be aware of self-promo rules; lead with the technical novelty (x402 mainnet wiring), not "use my API."
3. **GitHub awesome-lists** — submit PRs to:
   - `awesome-x402` (if it exists)
   - `awesome-ai-agents`
   - `awesome-mcp-servers`
   - `awesome-fastapi`
4. **mcpservers.org** / community MCP directories — submit the MCP wrapper.
5. **LinkedIn** — if you use it. Same as the dev.to but compressed to ~200 words; technical audience there responds to "I shipped X, here's what was non-obvious."
6. **Personal newsletter / Hashnode cross-post** — if you have a writing audience.

## 6. What to avoid

- Don't oversell the consumer side ("the future of APIs"). x402 is early; the realistic value prop right now is "interesting protocol, real product, small earnings stream, fun to consume from an agent."
- Don't bury the lede. The headline is: AI agents pay per request in USDC, no signup. Everything else is supporting.
- Don't post the same exact copy across all platforms — each has a tone. The drafts above are tuned for each.
- Don't paste the `PAYER_PRIVATE_KEY` example with a real-looking key; people copy-paste. The placeholder format here (`0x...funded-wallet-key...`) is intentional.
