# Reddit posts

Two communities, two framings. Reddit downvotes anything that smells like marketing, so both posts are written as **"here's a thing I made, here's what's interesting about it technically, here's my honest question for you."** Disclose authorship in the first line. No emojis, no hype, no exclamation marks.

**Best posting time:** Mon–Wed, 9am–noon Eastern. Avoid weekends (lower mod attention if it gets reported; lower engagement from working devs).

**Both posts assume the demo gif exists.** Both subs allow inline images via i.redd.it upload.

---

## 1. r/ClaudeAI

**Subreddit rules check:**
- Allows project showcases. Tag flair: "Productivity" or "MCP".
- Don't crosspost simultaneously with r/LocalLLaMA (mods notice patterns).
- Read the latest sidebar before posting — rules change.

### Title (Reddit allows 300 chars; keep it under 100 for mobile)

> I built an MCP server that lets Claude pull live USDA nutrition data — and it pays per call instead of using an API key

### Body

> *Disclosure: this is my project.*
>
> Quick context for anyone who's hit the "MCP servers that need API keys are a pain to share" wall: I built one that doesn't need a key at all. Claude pays a fraction of a cent per call in USDC stablecoins, and you fund a wallet with a few dollars up front.
>
> **What it does**
>
> Four tools that wrap USDA FoodData Central:
>
> - `nutrition_search` — find foods by name, get the FDA's internal IDs
> - `nutrition_detail` — full 13-nutrient per-100g profile
> - `nutrition_compare` — 2 to 5 foods side by side, with per-nutrient winners
> - `nutrition_recipe` — sum nutrition across a weighted recipe (great for meal planning)
>
> So you can ask Claude things like *"compare 100g of greek yogurt vs cottage cheese — which has more protein per calorie?"* and it actually fetches real USDA data instead of approximating.
>
> **Install**
>
> ```
> pip install nutriref-mcp
> ```
>
> Add to your `claude_desktop_config.json`:
>
> ```json
> {
>   "mcpServers": {
>     "nutriref": {
>       "command": "nutriref-mcp",
>       "env": {
>         "PAYER_PRIVATE_KEY": "0x...your-wallet-key...",
>         "NUTRIREF_BASE_URL": "https://nutriref.xyz"
>       }
>     }
>   }
> }
> ```
>
> **Cost in plain English**
>
> Calls cost $0.001 to $0.005 each. $5 of USDC = roughly 1,000–5,000 queries depending on which tools Claude picks. Wallet runs dry, calls stop — nothing surprises you on a bill.
>
> The wallet should be a throwaway funded only with what you're willing to spend. I use one with $2 in it for my own setup.
>
> **Demo**
>
> [INLINE GIF — same 30s recording]
>
> **Where it lives**
>
> Source + setup docs: github.com/Younghef/nutriref-api
> PyPI: pypi.org/project/nutriref-mcp
> Also on the official MCP registry and glama.ai if you're discovering through those.
>
> **My actual question for you**
>
> Is "pay-per-call with a prefunded wallet" something you'd actually use, or does adding crypto to your MCP setup feel like overkill? I'm genuinely undecided on whether the no-signup tradeoff is worth the wallet-funding step for most Claude users. Curious what people here think.

### Things to be ready for in comments

- *"Why not just use a free API?"* — USDA FDC has a free API; it requires an API key, rate-limits aggressively, and doesn't have `compare` or `recipe`. The paid one removes the key plus adds the derived endpoints.
- *"How do I get USDC on Base?"* — Coinbase or any onramp. Bridge from mainnet if you already have it. Don't get pulled into long crypto tutorials; link to Base's own onramp docs.
- *"This is just a wrapper, why charge?"* — fair. Lead with: caching layer, derived `compare`/`recipe` endpoints, MCP packaging, and uptime work. Be honest that the markup is small.

---

## 2. r/LocalLLaMA

**Subreddit rules check:**
- **Strict self-promo rules.** Read the rules in the sidebar before posting. Some weeks they're enforced harder than others.
- This is borderline because it requires a hosted API, which is the opposite of the sub's local-first ethos. Frame it as **an architecture pattern**, not as "use my product."
- Add the "Resources" flair, not "Discussion" — that signals lower self-interest.

### Title

> Pattern for monetizing MCP tools without API keys: x402 stablecoin micropayments on Base. Case study + open-source implementation.

### Body

> *Disclosure: this is my implementation. The post is mostly about the pattern, but I'll link the code at the end.*
>
> The MCP ecosystem has a distribution problem: every paid tool server today requires the user to sign up somewhere, get an API key, and paste it into their MCP config. That works fine for hobbyists but doesn't scale to *agents* — your CrewAI/LangChain/local-model workflow can't fill out signup forms.
>
> **The pattern**
>
> Use [x402](https://x402.org), an HTTP-402 micropayment protocol:
>
> 1. Server returns `402 Payment Required` with a price quote in USDC.
> 2. Client middleware signs an EIP-3009 gasless USDC authorization and retries.
> 3. Facilitator settles the transfer on Base mainnet (sponsors gas; agent only needs USDC, not ETH).
> 4. Server returns the actual response.
>
> No accounts. No keys. The agent's wallet IS the credential.
>
> **Why this is interesting for the local-LLM crowd**
>
> Even if your model runs locally, your *tools* don't. The MCP pattern is increasingly "local agent, distributed tools." x402 lets remote tool authors get paid without inventing a per-tool auth scheme, which makes it more likely that interesting paid tools (real-time data, paid APIs, premium feeds) actually get built for the MCP ecosystem.
>
> The local-vs-remote question isn't binary — you can run llama.cpp locally and still benefit from a marketplace of paid tools your agent can pull from.
>
> **My implementation as a worked example**
>
> I built **NutriRef** — USDA FoodData Central as four MCP tools, gated by x402. Calls cost $0.001–$0.005 in USDC. The agent runs locally (your Claude Code / your CrewAI / your local model with an MCP client), the tool runs at nutriref.xyz, payments settle on Base in under 2 seconds.
>
> - Source: github.com/Younghef/nutriref-api (MIT, FastAPI server + Python MCP wrapper)
> - PyPI: `pip install nutriref-mcp`
> - 30s demo gif: [LINK]
>
> The code is small enough to skim and copy — the x402 server-side integration is about 30 lines on top of FastAPI.
>
> **What I'm uncertain about**
>
> Two open questions I'd genuinely value local-LLM-builder opinions on:
>
> 1. **Wallet hygiene.** Right now the agent operator funds a wallet with a few dollars of USDC. Is that an acceptable UX for someone running a local agent, or does the moment a private key enters the loop the whole thing become a non-starter for most of you?
>
> 2. **Subscription vs per-call.** I priced per-call because per-call composes with x402. But would a $5/month flat fee with a regular API key actually be easier for you to integrate into a local agent stack? Per-call is interesting; I want to know if it's *useful*.
>
> Not looking for validation — looking for the version of this critique I haven't thought of yet.

### Things to be ready for in comments

- *"Why not just self-host the USDA data?"* — Valid. FDC is ~7GB; the value-add is the caching, the derived tools, and the no-key auth. Be honest: if you're shipping one product that uses this data, self-hosting is probably right.
- *"x402 is a Coinbase land grab"* — Acknowledge x402 came from Coinbase but the spec is open and there are independent facilitators in the works. Don't get defensive.
- *"Why Base and not [other chain]"* — Stablecoin transfers are cheap enough on Base that micropayments actually work; on Ethereum mainnet a $0.001 call costs $0.30 in gas. Solana would also work but the EVM tooling for x402 is more mature.
- **Mods may remove for self-promo.** If that happens, message them politely with the framing that it's an open pattern + open implementation, not a product launch. Don't repost.

---

## Posting sequence

If you also do Show HN:

- **Day 0:** Post Show HN (Tue/Wed morning ET).
- **Day 0, +2h:** Twitter thread, link to HN in the reply tags.
- **Day 1:** r/ClaudeAI post (lighter community, friendlier audience to warm up).
- **Day 2 or Day 3:** r/LocalLLaMA post (saving for when you have the HN/Reddit traction to mention as social proof in comments, if asked).
- **Day 3:** Base devrel cold email, leading with the HN+Reddit numbers.

Stagger so each post can stand on its own. Same-day cross-posting reads as marketing-campaign-flavored and gets downvoted on Reddit and removed by some mods.
