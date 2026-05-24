# Agent registry submissions

Paste-ready text for the four submissions we identified to broaden agent-side
discovery. Each section is independent — submit in whatever order works for
you. Replace the obvious placeholders if you want to tweak voice.

---

## 1. mcp.so

**Where:** https://mcp.so/submit (their submission form). If the form has
changed by the time you read this, mcp.so also accepts PRs to its
[server-list repo](https://github.com/chatmcp/mcp-directory).

**Form fields → values:**

- **Name:** `NutriRef`
- **Description (short):** `Pay-per-call USDA nutrition data for AI agents. Each tool call charges USDC on Base mainnet via x402 — no signup, no API keys.`
- **Repository URL:** `https://github.com/Younghef/nutriref-api`
- **Homepage:** `https://nutriref.xyz`
- **Category:** `Data Platforms` (or `API` if available)
- **Tags:** `nutrition`, `usda`, `x402`, `paid`, `food`, `agents`
- **Author:** Your GitHub handle
- **Install command:**
  ```
  git clone https://github.com/Younghef/nutriref-api.git
  cd nutriref-api && pip install -e ".[mcp]"
  ```
- **Configuration (longer field if available):**
  ```json
  {
    "mcpServers": {
      "nutriref": {
        "command": "python",
        "args": ["-m", "mcp_server"],
        "env": {
          "PAYER_PRIVATE_KEY": "0x...funded-base-mainnet-wallet-key...",
          "NUTRIREF_BASE_URL": "https://nutriref.xyz"
        }
      }
    }
  }
  ```

If the form takes a longer description, this works:

> NutriRef exposes the USDA FoodData Central nutrition database as four MCP
> tools (`nutrition_search`, `nutrition_detail`, `nutrition_compare`,
> `nutrition_recipe`). Instead of an API key or subscription, each call
> charges a small amount of USDC ($0.001–$0.005) on Base mainnet via the
> x402 micropayment protocol. The agent operator funds a wallet once with
> USDC — gas is sponsored by the facilitator, so the wallet only needs the
> stablecoin balance. Returns normalized per-100g nutrition across 13
> tracked nutrients; missing nutrients are explicit `null`. Live API at
> https://nutriref.xyz, OpenAPI at https://nutriref.xyz/openapi.json.

---

## 2. Smithery (smithery.ai)

Smithery now publishes stdio servers as **MCPB bundles** via their CLI,
not via a GitHub-connect form. The repo already has everything needed:
`mcpb/` (bundle source), `scripts/build-mcpb.sh` (one-command rebuild),
and a manifest declaring the user config schema.

### One-time: log in to Smithery
```bash
npx @smithery/cli login
```
Opens a browser for OAuth. Smithery's namespace for your account is
`derekhefley` (as you saw on the publish page).

### Build and publish
```bash
./scripts/build-mcpb.sh
npx @smithery/cli mcp publish ./build/nutriref.mcpb -n derekhefley/nutriref
```
The build script refreshes the `mcp_server/` copy inside the bundle,
validates the manifest, and produces `build/nutriref.mcpb` (~4 kB).
The publish command uploads it under your namespace.

### What Smithery will display (sourced from manifest.json)

- **Display name:** NutriRef
- **Description:** "Pay-per-call USDA nutrition data for AI agents (x402 + USDC on Base)."
- **Long description, license, repository, homepage, keywords, and tools** all flow from `mcpb/manifest.json` — no UI form to fill.
- **User config the operator fills out:** `payer_private_key` (sensitive, required) and `nutriref_base_url` (optional, default `https://nutriref.xyz`).

### Future updates

Whenever the MCP server code changes, rebuild and republish:
```bash
./scripts/build-mcpb.sh
npx @smithery/cli mcp publish ./build/nutriref.mcpb -n derekhefley/nutriref
```
Smithery's CLI handles version bumps if you increment `version` in
`mcpb/manifest.json`.

---

## 3. awesome-mcp-servers (PR)

**Where:** https://github.com/modelcontextprotocol/awesome-mcp-servers
(canonical list; community-maintained).

**Steps:**
1. Fork the repo.
2. Read the existing categories in `README.md` and find the best fit.
   As of this writing the most likely homes are `🗄️ <a name="data-platforms">Data Platforms</a>` or `📂 <a name="data-platforms">Data and File Systems</a>`, depending on current organization.
3. Add the entry below in **alphabetical order** within that category.
4. Open a PR with the title and body below.

**Entry to add (markdown, single line):**
```markdown
- [Younghef/nutriref-api](https://github.com/Younghef/nutriref-api) 🐍 ☁️ - USDA FoodData Central nutrition data, gated by x402 micropayments. Each tool call charges $0.001–$0.005 in USDC on Base mainnet — no signup, no API keys. Four tools: search, detail, compare, recipe.
```

(`🐍` = Python implementation; `☁️` = cloud/SaaS; adjust if the legend has changed.)

**PR title:**
```
Add NutriRef — pay-per-call USDA nutrition (x402 + USDC on Base)
```

**PR body:**
```markdown
This adds NutriRef under [Category Name TBD — pick the best fit].

NutriRef is a monetized MCP server backed by the USDA FoodData Central
database. Each tool call charges a small amount of USDC ($0.001–$0.005)
on Base mainnet via the x402 micropayment protocol — there's no signup,
no API key, no rate-limit table. Agent operators fund a wallet once
with USDC and the rest happens automatically (gas is sponsored by the
x402 facilitator).

Four tools exposed:
- `nutrition_search` — find foods by name, get `fdc_id` and macros
- `nutrition_detail` — full per-100g nutrition (13 nutrients)
- `nutrition_compare` — side-by-side with per-nutrient winners
- `nutrition_recipe` — scale and sum across weighted ingredients

The server itself is at https://nutriref.xyz; the MCP wrapper is in
`mcp_server/` of the repo. An end-to-end Claude example lives in
`examples/meal-planner/`.

License: MIT.
```

---

## 4. PulseMCP

**Where:** https://www.pulsemcp.com/submit (or wherever their current
submission flow lives — check the homepage). PulseMCP is a curated
directory; it sometimes accepts via form and sometimes via PR to
[its server registry](https://github.com/PulseMCP/community).

**Form / submission text:**

- **Server name:** `NutriRef`
- **Tagline (one line):** `Pay-per-call USDA nutrition data for AI agents.`
- **Description:**
  > NutriRef is a monetized MCP server that wraps the USDA FoodData
  > Central nutrition database. Each tool call charges $0.001–$0.005
  > in USDC on Base mainnet via the x402 micropayment protocol — no
  > signup, no API keys, no rate limiters (the wallet IS the rate
  > limiter). Four tools: search, detail (full per-100g nutrition,
  > 13 nutrients), compare (2–5 foods side by side with per-nutrient
  > winners), and recipe (scale and sum ingredient nutrition). Live
  > API: https://nutriref.xyz. Source + install:
  > https://github.com/Younghef/nutriref-api.
- **Author:** Your GitHub handle
- **Repository:** `https://github.com/Younghef/nutriref-api`
- **License:** MIT
- **Install command:** same as mcp.so above
- **Configuration:** same JSON block as mcp.so above

---

## 5. (Optional) awesome-ai-agents

**Honest caveat:** awesome-ai-agents primarily lists agent **frameworks
and agents**, not tools/APIs that agents consume. NutriRef is the latter,
so the fit is weaker than the three above. The strongest pitch is to
submit `examples/meal-planner/` (an actual Claude agent that uses
NutriRef) as the entry, not NutriRef itself.

**Where:** https://github.com/e2b-dev/awesome-ai-agents — fork, add an
entry to whichever subcategory fits (probably `Build Your Own` or a
`Tools & APIs` section if it now exists). Decide whether to bother
based on whether you find such a section.

**Entry (markdown):**
```markdown
- [NutriRef meal planner](https://github.com/Younghef/nutriref-api/tree/master/examples/meal-planner) — Claude agent that plans daily meals using the NutriRef nutrition API (x402-paid, USDC on Base). Demonstrates LLM tool-use + agentic micropayments end to end.
```

If you can't find a sensible category, skip this one. It's the weakest
fit of the four.

---

## Order to submit

1. **awesome-mcp-servers PR** — biggest organic traffic of the four.
2. **Smithery** — increasingly the default for auto-installable MCP servers.
3. **mcp.so** — broad reach, lower bar to listing.
4. **PulseMCP** — smaller audience but curated, signal-rich.

All four can go in the same session if you have ~30 minutes; the bottleneck
will be the awesome-mcp-servers PR review.

## After submission

For Smithery and mcp.so, you may receive a config-validation or category
question. Reply same-day — these reviews move fast.

For the awesome-mcp-servers PR, expect a maintainer to comment on category
placement or formatting. Don't argue placement; whatever they prefer is
fine. The goal is the link to exist, not its location.
