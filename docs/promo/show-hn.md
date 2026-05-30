# Show HN draft — NutriRef

## Title (80 chars max)

**Primary pick:**
> Show HN: NutriRef – USDA nutrition for AI agents, paid per call in USDC on Base

(76 chars. Concrete, names the protocol's chain, hints at novelty.)

**Alternates:**
- Show HN: An MCP server agents pay $0.001 in USDC per call (no signup, no keys)
- Show HN: NutriRef – first pay-per-call MCP server, gated by x402 stablecoin payments

## URL field

`https://nutriref.xyz` (the live API). HN displays this prominently.

## Body

> I built a paid API that AI agents can use without signing up or holding an API key.
>
> The problem: agents (Claude, custom LangChain/CrewAI builds, etc.) need access to data APIs, but they can't fill out a signup form, verify an email, or rotate a key. Either someone has to provision a key for the agent up-front, or the API has to be free.
>
> The fix: x402 — an HTTP 402 micropayment protocol from Coinbase that lets servers say "pay $0.001 in USDC to access this endpoint" and lets clients (or their wallet middleware) sign a gasless EIP-3009 USDC authorization and retry. No accounts. No key vaulting. The agent's wallet pays per call.
>
> NutriRef wraps USDA FoodData Central as four endpoints:
> - `nutrition_search` ($0.001) — find foods by name → fdc_id
> - `nutrition_detail` ($0.002) — full 13-nutrient per-100g profile
> - `nutrition_compare` ($0.003) — 2–5 foods side by side with per-nutrient winners
> - `nutrition_recipe` ($0.005) — sum nutrition across weighted ingredients
>
> It also ships as an MCP server, so Claude Desktop / Claude Code / any MCP-speaking agent can install it (`pip install nutriref-mcp` or `uvx nutriref-mcp`) and use the four tools natively. The agent operator funds a Base mainnet wallet with a few dollars of USDC and the agent pays per query.
>
> Listed on the official MCP registry, Glama, and awesome-mcp-servers. Source: https://github.com/Younghef/nutriref-api
>
> Honest about state: it's live, the payments work on Base mainnet, and the data comes straight from USDA FDC. The agent UX is the experimental part — I'd love feedback on whether per-call stablecoin pricing actually fits how you're building agents, or whether subscription-style billing would be easier to integrate.

(~290 words; HN tolerates this length when the topic warrants it. Cut the last paragraph if you want to come in tighter.)

## Comment to post 5 minutes after submission

HN front-page algorithm rewards early author engagement. Have this ready:

> Quick context I left out: the facilitator on Base sponsors gas, so the agent's wallet only needs USDC — no ETH for gas. That removes the biggest "agents holding crypto" footgun. Settlement is usually <2 seconds.
>
> Happy to answer anything about the x402 client integration, the MCP server design, or why I priced calls at $0.001–$0.005 instead of flat $0.01.

## When to post

- **Tue–Thu, 8–10am Eastern** (~5–7am Pacific). HN's audience is most active right when the West Coast wakes up, and there's less competition than the midday spike. Avoid Mondays (catch-up day, post backlog crowds you out) and Fridays (drops into the weekend).
- Make sure you can be at your computer for the first 2–3 hours to answer comments — HN algorithm heavily weights comment velocity and quality.

## Pre-flight checklist

- [ ] Demo gif/video uploaded (Imgur or Vimeo — HN doesn't embed but commenters will click)
- [ ] README opens with the badge + an animated demo + the `pip install` line (anyone clicking the GitHub link from HN judges in <10 seconds)
- [ ] Wallet on `nutriref.xyz` has enough USDC float for traffic spikes (a few dollars covers thousands of calls)
- [ ] Status page or "is it up?" check ready in case it gets hugged
- [ ] You've used HN before (account >30 days old + some comment karma) — brand-new accounts get filtered
