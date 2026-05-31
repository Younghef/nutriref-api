# Coinbase / Base devrel cold pitch

**Goal:** get a retweet, quote-tweet, or newsletter mention from the Base or x402 team. They actively hunt for x402 case studies. You are exactly the kind of "real shipped thing on mainnet" they want to point at.

**Best timing:** the day after your Show HN post lands. Lead with social proof.

## Who to message

In rough order of likely-to-respond:

1. **`devrel@base.org`** — direct email, low risk, gets read.
2. **DM on X to `@coinbasedev` and `@base`** — official accounts; community team monitors.
3. **`@jessepollak` on X** — Base lead, occasionally amplifies builders directly. Don't expect a reply but a like/RT is plausible.
4. **x402 GitHub Discussions** — https://github.com/coinbase/x402/discussions — post a "Show & Tell" thread linking the gif. Their team reads it.
5. **Base Discord** (#showcase channel) — invite via base.org. Drop the gif + one paragraph.

## Pitch (~150 words — adapt per channel)

> Subject: Live x402 case study: AI agents paying USDC for nutrition data on Base
>
> Hi — I built **NutriRef**, a USDA FoodData Central API gated by x402, live on Base mainnet. Agents pay $0.001–$0.005 in USDC per call, no signup, no API keys. The agent operator funds a wallet with a few dollars of USDC and the agent transacts per query.
>
> It's also packaged as an MCP server (on PyPI, the official MCP registry, and Glama), so any Claude Desktop / Claude Code / LangChain agent can install it and start paying for queries in one line: `pip install nutriref-mcp`.
>
> 30-second demo: [GIF/VIDEO LINK]
> Show HN: [HN LINK — once it's posted]
> Source: https://github.com/Younghef/nutriref-api
>
> If this is the kind of x402 build you're looking to amplify, happy to write it up as a longer case study, do a livestream, or whatever's useful. Either way, just wanted you to see it shipped.
>
> — Derek (Younghef)

## DM-length variant (X, 280 chars)

> Built an x402-gated USDA nutrition API for AI agents — live on Base, $0.001/call in USDC, no signup. Packaged as an MCP server (`pip install nutriref-mcp`). 30s demo: [LINK]. Open to writing it up as a case study if useful.

## Why this works

- **You shipped to mainnet.** Most x402 demos are testnet or sketches.
- **You have a real second protocol (MCP) using it.** That makes it a layered story, not just "I called the x402 SDK."
- **It's already discoverable** via three registries. They can verify in 30 seconds.
- **You're not asking for money or grants** — just amplification. Cheap for them to say yes.

## Don't

- Don't ask for a retweet directly. Show the work; let them choose.
- Don't tag Brian Armstrong. He doesn't run devrel and it reads spammy.
- Don't send the same pitch to all five channels on the same day. Email first, wait 48h, then escalate to social.
