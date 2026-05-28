# nutriref-mcp

MCP server for **[NutriRef](https://nutriref.xyz)** — pay-per-call USDA FoodData Central nutrition for AI agents, gated by [x402](https://www.x402.org/) micropayments in USDC on Base. No signup, no API keys.

It exposes four tools:

| Tool | What it does | Price |
|---|---|---|
| `nutrition_search` | Find foods by name, get `fdc_id` + macros | $0.001 |
| `nutrition_detail` | Full per-100g profile (13 nutrients) for one food | $0.002 |
| `nutrition_compare` | Compare 2–5 foods with per-nutrient winners | $0.003 |
| `nutrition_recipe` | Scale and sum nutrition across weighted ingredients | $0.005 |

## Install

```bash
pip install nutriref-mcp
```

Or run without installing:

```bash
uvx nutriref-mcp
```

## Configure your MCP client

Add this to your client config (Claude Desktop's `claude_desktop_config.json`, Claude Code's MCP settings, etc.):

```json
{
  "mcpServers": {
    "nutriref": {
      "command": "nutriref-mcp",
      "env": {
        "PAYER_PRIVATE_KEY": "0x...your-funded-wallet-key...",
        "NUTRIREF_BASE_URL": "https://nutriref.xyz"
      }
    }
  }
}
```

`PAYER_PRIVATE_KEY` is the private key of a Base mainnet wallet holding USDC — the wallet pays for each tool call. Use a dedicated wallet funded only with what you're willing to spend. `NUTRIREF_BASE_URL` is optional and defaults to `https://nutriref.xyz`.

## License

MIT
