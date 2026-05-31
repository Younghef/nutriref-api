# Twitter / X launch thread

**Format:** 6 tweets. Tweet 1 carries the demo gif and the hook. Each follow-up adds one idea. Last tweet is the ask.

**Best posting time:** Tue–Thu, 9–11am Eastern (overlaps US tech audience waking up + EU still online).

**Tag economy:** tag accounts in *replies*, not the headline tweet. Tagging in tweet 1 reduces reach (Twitter's algorithm suppresses it). Mentions in body text are fine.

---

## Tweet 1 — hook + gif

> AI agents can't sign up for API keys.
>
> So I built a USDA nutrition API that agents pay for in stablecoins instead. $0.001 per call, USDC on Base, no accounts, no auth flow.
>
> Demo ↓
>
> [ATTACH 30s GIF]

(263 chars. The gif IS the hook — the text just frames it.)

## Tweet 2 — what's underneath

> It's built on x402, an HTTP-402 micropayment protocol from Coinbase.
>
> Server says "pay $0.001 to access this endpoint."
> Client signs a gasless USDC authorization (EIP-3009) and retries.
> Settles on Base in <2 seconds. Facilitator sponsors the gas.

## Tweet 3 — the agent angle

> The interesting part isn't the nutrition data — it's that *agents can pay for it without a human in the loop*.
>
> Fund a wallet with $5 in USDC. The agent has a budget. It transacts per query. When the wallet empties, the agent stops calling. Clean.

## Tweet 4 — what you can actually do with it

> Four tools, exposed as MCP so Claude (or any MCP agent) uses them natively:
>
> • `nutrition_search` – find foods by name ($0.001)
> • `nutrition_detail` – full per-100g profile, 13 nutrients ($0.002)
> • `nutrition_compare` – 2–5 foods side by side ($0.003)
> • `nutrition_recipe` – sum a weighted recipe ($0.005)

## Tweet 5 — install

> One line to install:
>
> `pip install nutriref-mcp`
>
> Or run on demand without installing: `uvx nutriref-mcp`
>
> Add it to your MCP client config, fund a Base wallet with USDC, and your agent has access to USDA FoodData Central.
>
> Source: github.com/Younghef/nutriref-api

## Tweet 6 — the ask

> Genuinely curious: if you're building agents, would per-call stablecoin pricing be easier or harder for you to integrate than monthly subscriptions?
>
> Reply or DM — I'm trying to figure out whether this billing model fits how teams are actually building agent products.

## Suggested reply tags (in REPLY thread, not the headline)

After posting, reply to your own tweet 1 with:

> cc @AnthropicAI (MCP), @base / @coinbasedev (x402), @jessepollak — if any of this is useful as an x402 case study, happy to write it up further.

This gets you in their notifications without algorithmic penalty on the headline tweet.

## Repurposing

- **LinkedIn:** combine tweets 1–5 into one post, drop the demo gif, end with the ask. Better LinkedIn engagement than threads.
- **Mastodon (@fosstodon, @hachyderm.io):** same content but lead with the "MCP server" angle, not the "stablecoins" angle — different audience priors.
- **MCP Discord #showcase:** post tweet 1 + gif as the message; let people click through to the thread for detail.
