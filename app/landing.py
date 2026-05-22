"""Public landing page served at /.

A single self-contained HTML page describing NutriRef to a human developer
who lands at https://nutriref.xyz/ — what it is, the endpoints, prices, and
a copy-pasteable agent example.
"""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from app.config import settings

router = APIRouter()


def _html() -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>NutriRef — pay-per-call USDA nutrition API for AI agents</title>
  <meta name="description" content="Structured USDA FoodData Central nutrition for AI agents. Pay $0.001-$0.005 per request in USDC via x402. No signup, no API keys." />
  <meta property="og:title" content="NutriRef — pay-per-call USDA nutrition API for AI agents" />
  <meta property="og:description" content="Structured USDA FoodData Central nutrition for AI agents. Pay $0.001-$0.005 per request in USDC via x402. No signup, no API keys." />
  <meta property="og:type" content="website" />
  <meta property="og:url" content="https://nutriref.xyz/" />
  <meta name="twitter:card" content="summary" />
  <style>
    :root {{
      --bg: #fafaf7;
      --fg: #1a1a1a;
      --muted: #6b6b6b;
      --accent: #0a6e3a;
      --code-bg: #f0efea;
      --border: #e3e2dc;
    }}
    @media (prefers-color-scheme: dark) {{
      :root {{
        --bg: #1a1a1a;
        --fg: #ededed;
        --muted: #9c9c9c;
        --accent: #4ade80;
        --code-bg: #262626;
        --border: #333333;
      }}
    }}
    * {{ box-sizing: border-box; }}
    html, body {{ margin: 0; padding: 0; background: var(--bg); color: var(--fg); }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      line-height: 1.55;
      -webkit-font-smoothing: antialiased;
    }}
    main {{ max-width: 760px; margin: 0 auto; padding: 56px 24px 96px; }}
    header {{ margin-bottom: 40px; }}
    h1 {{ font-size: 2rem; margin: 0 0 8px; letter-spacing: -0.02em; }}
    h1 .price {{ color: var(--accent); font-weight: 500; }}
    .tagline {{ color: var(--muted); margin: 0; font-size: 1.05rem; }}
    h2 {{
      font-size: 1.15rem; margin: 40px 0 12px;
      letter-spacing: -0.01em;
      padding-bottom: 6px; border-bottom: 1px solid var(--border);
    }}
    code, pre {{ font-family: "SF Mono", Menlo, Consolas, "Liberation Mono", monospace; font-size: 0.9rem; }}
    code {{ background: var(--code-bg); padding: 2px 6px; border-radius: 4px; }}
    pre {{
      background: var(--code-bg); padding: 16px 18px; border-radius: 8px;
      overflow-x: auto; border: 1px solid var(--border); margin: 12px 0;
    }}
    pre code {{ background: none; padding: 0; }}
    table {{ width: 100%; border-collapse: collapse; margin: 8px 0; font-size: 0.95rem; }}
    th, td {{ text-align: left; padding: 10px 12px; border-bottom: 1px solid var(--border); }}
    th {{ font-weight: 600; color: var(--muted); font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.04em; }}
    td.method {{ font-family: "SF Mono", Menlo, monospace; color: var(--accent); font-weight: 600; font-size: 0.85rem; }}
    td.path {{ font-family: "SF Mono", Menlo, monospace; }}
    td.price {{ font-family: "SF Mono", Menlo, monospace; color: var(--accent); }}
    .kv {{ font-size: 0.95rem; color: var(--muted); }}
    .kv strong {{ color: var(--fg); font-weight: 500; }}
    .kv code {{ word-break: break-all; }}
    a {{ color: var(--accent); }}
    footer {{ margin-top: 64px; padding-top: 24px; border-top: 1px solid var(--border); color: var(--muted); font-size: 0.85rem; }}
    footer a {{ margin-right: 14px; }}
  </style>
</head>
<body>
<main>
  <header>
    <h1>NutriRef <span class="price">— pay-per-call USDA nutrition for AI agents</span></h1>
    <p class="tagline">Structured FoodData Central data behind <a href="https://www.x402.org/">x402</a> micropayments. No signup, no API keys, no auth flows — agents pay $0.001 – $0.005 per request in USDC on Base.</p>
  </header>

  <h2>Endpoints</h2>
  <table>
    <thead><tr><th>Method</th><th>Path</th><th>Price</th><th>Returns</th></tr></thead>
    <tbody>
      <tr><td class="method">GET</td><td class="path">/v1/nutrition/search?q=&amp;limit=</td><td class="price">$0.001</td><td>Ranked food matches (fdc_id + macros)</td></tr>
      <tr><td class="method">GET</td><td class="path">/v1/nutrition/detail/{{fdc_id}}</td><td class="price">$0.002</td><td>Full normalized nutrition (13 nutrients)</td></tr>
      <tr><td class="method">POST</td><td class="path">/v1/nutrition/compare</td><td class="price">$0.003</td><td>2–5 foods side by side + per-nutrient winners</td></tr>
      <tr><td class="method">POST</td><td class="path">/v1/nutrition/recipe</td><td class="price">$0.005</td><td>Scaled + summed nutrition for a recipe</td></tr>
    </tbody>
  </table>

  <h2>How payment works</h2>
  <p>An x402-aware HTTP client handles it automatically. Unpaid requests return <code>402 Payment Required</code> with payment instructions; the client signs a gasless USDC authorization (EIP-3009) and retries. The facilitator settles on-chain.</p>

  <h2>Call it from Python</h2>
<pre><code>from x402.client import x402Client
from x402.http.clients.httpx import wrapHttpxWithPayment
from x402.mechanisms.evm.exact import register_exact_evm_client
from eth_account import Account
import asyncio

account = Account.from_key("0x...your-funded-wallet-key...")  # needs USDC on Base
client = x402Client(); register_exact_evm_client(client, account)

async def main():
    async with wrapHttpxWithPayment(client, base_url="https://nutriref.xyz") as http:
        r = await http.get("/v1/nutrition/detail/2012128")
        print(r.json())

asyncio.run(main())</code></pre>

  <h2>Network</h2>
  <p class="kv">
    <strong>Chain</strong> Base mainnet (chain id 8453)<br />
    <strong>Asset</strong> USDC — <code>0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913</code><br />
    <strong>Receiver</strong> <code>{settings.x402_receiver_address}</code>
  </p>

  <h2>Use it from Claude / MCP agents</h2>
  <p>NutriRef ships an MCP server wrapper. Any agent that speaks MCP (Claude Desktop, Claude Code, etc.) plugs it in with one config block:</p>
<pre><code>{{
  "mcpServers": {{
    "nutriref": {{
      "command": "python",
      "args": ["-m", "mcp_server"],
      "env": {{
        "PAYER_PRIVATE_KEY": "0x...your-funded-wallet-key...",
        "NUTRIREF_BASE_URL": "https://nutriref.xyz"
      }}
    }}
  }}
}}</code></pre>
  <p>Source &amp; install: <a href="https://github.com/Younghef/nutriref-api">github.com/Younghef/nutriref-api</a> (<code>pip install ".[mcp]"</code>).</p>

  <h2>Machine-readable</h2>
  <p><a href="/openapi.json">/openapi.json</a> — full OpenAPI spec ·
     <a href="/docs">/docs</a> — Swagger UI ·
     <a href="/.well-known/x402">/.well-known/x402</a> — x402 Bazaar discovery</p>

  <footer>
    Built with <a href="https://www.x402.org/">x402</a> · USDA data from <a href="https://fdc.nal.usda.gov/">FoodData Central</a>
  </footer>
</main>
</body>
</html>
"""


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
async def index() -> HTMLResponse:
    return HTMLResponse(content=_html())
