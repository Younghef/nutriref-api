# Agent registry submissions

Paste-ready text for the four submissions we identified to broaden agent-side
discovery. Each section is independent — submit in whatever order works for
you. Replace the obvious placeholders if you want to tweak voice.

---

## 1. mcp.so

**Where:** mcp.so submissions go through a single tracking issue on the
mirror repo — https://github.com/chatmcp/mcp-directory/issues/1 — by
adding a comment. The maintainers ingest comments and surface entries on
https://mcp.so. There is no web form to fill.

**Steps:**

1. Open the issue: https://github.com/chatmcp/mcp-directory/issues/1
2. Click **Comment** at the bottom.
3. Paste the markdown block below verbatim, then **Comment**.
4. Done. Your entry should appear on mcp.so within a few days.

**Paste this:**

````markdown
## NutriRef — pay-per-call USDA nutrition for AI agents

**USDA FoodData Central nutrition data, gated by x402 micropayments — no signup, no API keys.**

NutriRef wraps the USDA FoodData Central database behind the x402 micropayment
protocol. Each tool call charges $0.001–$0.005 in USDC on Base mainnet — the
agent operator funds a wallet once and the rest is automatic (gas is sponsored
by the facilitator via EIP-3009 gasless authorizations).

- **Repo:** https://github.com/Younghef/nutriref-api
- **Live API:** https://nutriref.xyz
- **OpenAPI spec:** https://nutriref.xyz/openapi.json
- **LLM-readable summary:** https://nutriref.xyz/llms.txt
- **x402 discovery:** https://nutriref.xyz/.well-known/x402
- **Transport:** stdio (Python MCP server, MCPB-packaged for one-click install)
- **License:** MIT
- **Auth:** None — payment via x402 in USDC on Base mainnet.

### Tools (4)

| Tool | Description | Price |
|---|---|---|
| `nutrition_search` | Find foods in the USDA database by free-text name; returns fdc_id + macros | $0.001 |
| `nutrition_detail` | Full per-100g nutrition (13 nutrients) for one food by fdc_id | $0.002 |
| `nutrition_compare` | Side-by-side comparison of 2–5 foods with per-nutrient winners | $0.003 |
| `nutrition_recipe` | Scale and sum nutrition across weighted ingredients | $0.005 |

### Quick start (MCP)

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

Install: `git clone https://github.com/Younghef/nutriref-api.git && cd nutriref-api && pip install -e ".[mcp]"`

### Example: Claude agent using NutriRef

`examples/meal-planner/` in the repo is a ~150-line Claude agent that uses
the four tools to plan a day of meals against a calorie/protein goal.
````

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

**Where:** https://www.pulsemcp.com/submit

PulseMCP's form is **minimal** — just a submission-type radio and a single
URL field. PulseMCP scrapes the linked repo for the rest (README, license,
tools, badges). Our README is already pitched for this; nothing else to
prepare.

**Field-by-field:**

| Field | Value |
|---|---|
| "What would you like to submit?" | **MCP Server** |
| URL | `https://github.com/Younghef/nutriref-api` |

Click submit. That's the whole flow. The entry typically appears within a
few days after PulseMCP's processing cycle.

### Bonus: the route PulseMCP prefers

PulseMCP's submit page notes they **automatically ingest entries from the
[official MCP registry](https://github.com/modelcontextprotocol/registry)
daily**. Listing there gives you PulseMCP + several other downstream
directories for free, and is the canonical home for MCP server metadata.

That submission is the **official MCP registry** flow described in section 5 below — recommended next, since one publish there propagates to PulseMCP and several other downstream directories automatically.

---

## 5. Official MCP registry (modelcontextprotocol/registry)

**Why this matters:** PulseMCP, Smithery's discovery page, and several other directories auto-ingest from the official registry daily. One publish here is the highest-leverage submission of the set.

The repo already has `server.json` at the root with everything except the bundle SHA-256 (which changes per build) and the release URL (depends on the tag you cut).

### One-time setup

1. Install the publisher CLI:
   ```bash
   git clone https://github.com/modelcontextprotocol/registry.git /tmp/mcp-registry
   cd /tmp/mcp-registry && make publisher
   # binary lands at /tmp/mcp-registry/bin/mcp-publisher
   ```
   (Or grab a release binary from https://github.com/modelcontextprotocol/registry/releases if available.)

2. Log in via GitHub:
   ```bash
   mcp-publisher login github
   ```
   This is what authorizes the `io.github.younghef/` namespace.

### Each release

1. Build the bundle and capture its SHA-256 (the build script prints it):
   ```bash
   ./scripts/build-mcpb.sh
   # → sha256: <64 hex chars>
   ```

2. Cut a GitHub release and attach the bundle:
   ```bash
   gh release create v0.2.0 build/nutriref.mcpb \
     --title "v0.2.0" --notes "MCPB bundle for MCP registry."
   ```
   (Bump the tag for each new version. The download URL pattern is
   `https://github.com/Younghef/nutriref-api/releases/download/<tag>/nutriref.mcpb`.)

3. Update `server.json`:
   - `version` and `packages[0].version` → match the tag (without the leading `v`)
   - `packages[0].identifier` → the release asset URL
   - `packages[0].fileSha256` → the sha256 printed by the build script

4. Validate and publish:
   ```bash
   mcp-publisher validate    # optional but cheap
   mcp-publisher publish
   ```

The entry appears at `https://registry.modelcontextprotocol.io/v0/servers?search=nutriref` within minutes, and downstream directories pick it up on their next ingest cycle (typically <24h for PulseMCP).

### Namespace note

`io.github.younghef/nutriref` is reserved by GitHub OAuth — only the `Younghef` GitHub account can publish under it. If you ever want a custom namespace (e.g., `xyz.nutriref/nutriref`), the registry supports DNS or HTTP verification on `nutriref.xyz`; see [registry docs](https://github.com/modelcontextprotocol/registry/tree/main/docs).

---

## 6. Glama.ai

**Where:** https://glama.ai/mcp/servers — click **Add Server** in the top-right.

Glama's form is short. Most fields are scraped from the linked GitHub repo (README, license, tools list), so the README pitch we already have is doing the work.

**Field-by-field:**

| Field | Value |
|---|---|
| Repository URL | `https://github.com/Younghef/nutriref-api` |
| Category | **Finance** or **APIs** (whichever Glama currently lists; NutriRef is a paid API, so either fits) |
| Short description | Pay-per-call USDA nutrition for AI agents — x402 micropayments, USDC on Base, no signup. |

Glama also auto-discovers servers from the official registry, so this submission becomes redundant once section 5 is live. Do it if you want the listing now rather than waiting on the next ingest.

---

## 7. (Optional) awesome-ai-agents

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

1. **Official MCP registry (section 5)** — highest leverage; PulseMCP and others auto-ingest from here, so skip section 4 if you do this.
2. **Smithery** — increasingly the default for auto-installable MCP servers.
3. **awesome-mcp-servers PR** — biggest organic traffic of the static lists.
4. **mcp.so** — broad reach, lower bar to listing.
5. **Glama** — quick add-server form, redundant once #1 propagates.
6. **PulseMCP** — only if #1 hasn't propagated yet (it auto-ingests).

All can go in one ~45-minute session; the bottleneck is the awesome-mcp-servers PR review.

## After submission

For Smithery and mcp.so, you may receive a config-validation or category
question. Reply same-day — these reviews move fast.

For the awesome-mcp-servers PR, expect a maintainer to comment on category
placement or formatting. Don't argue placement; whatever they prefer is
fine. The goal is the link to exist, not its location.
