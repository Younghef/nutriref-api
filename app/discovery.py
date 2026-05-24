"""Discovery endpoint at /.well-known/x402.

Publishes a machine-readable directory of NutriRef's paid resources using the
x402 Bazaar discovery vocabulary. Any crawler / aggregator that speaks Bazaar
can ingest this.

Note: the canonical Bazaar protocol catalogs resources via the `extensions`
field that the server attaches to its 402 challenge — `fastapi-x402` does not
yet surface that field, so this well-known document is a parallel mechanism.
The shape of each resource here matches what would be emitted in-band when
the upstream gains extensions support.
"""

from fastapi import APIRouter
from fastapi.responses import PlainTextResponse, Response
from x402.extensions.bazaar import OutputConfig, declare_discovery_extension

from app.config import settings

router = APIRouter()


_BASE_URL = "https://nutriref.xyz"
_USDC_BASE_MAINNET = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"


def _resource(method: str, path: str, price_usd: str, description: str, discovery_ext: dict) -> dict:
    return {
        "url": _BASE_URL + path,
        "method": method,
        "description": description,
        "price": {"asset": "USDC", "address": _USDC_BASE_MAINNET, "amount": price_usd, "network": "base"},
        "payTo": settings.x402_receiver_address,
        "discovery": discovery_ext,
    }


def _search_discovery() -> dict:
    return declare_discovery_extension(
        input={"q": "banana", "limit": 10},
        input_schema={
            "type": "object",
            "properties": {
                "q": {"type": "string", "description": "Free-text food name to search."},
                "limit": {"type": "integer", "minimum": 1, "maximum": 50, "default": 10},
            },
            "required": ["q"],
        },
        output=OutputConfig(
            example={
                "query": "banana",
                "count": 1,
                "results": [{"fdc_id": 2012128, "description": "BANANA", "calories": 312.0, "protein": 12.5}],
            }
        ),
    )


def _detail_discovery() -> dict:
    return declare_discovery_extension(
        input=None,
        path_params_schema={
            "type": "object",
            "properties": {"fdc_id": {"type": "integer", "description": "USDA FoodData Central ID."}},
            "required": ["fdc_id"],
        },
        output=OutputConfig(
            example={
                "fdc_id": 2012128,
                "description": "BANANA",
                "calories": 312.0,
                "protein": 12.5,
                "fat": 6.25,
                "carbs": 40.62,
                "fiber": 6.2,
                "potassium": None,
            }
        ),
    )


def _compare_discovery() -> dict:
    return declare_discovery_extension(
        input={"fdc_ids": [2012128, 2011468]},
        input_schema={
            "type": "object",
            "properties": {
                "fdc_ids": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "minItems": 2,
                    "maxItems": 5,
                }
            },
            "required": ["fdc_ids"],
        },
        body_type="json",
        output=OutputConfig(
            example={
                "foods": [{"fdc_id": 2012128, "protein": 12.5}, {"fdc_id": 2011468, "protein": 0.0}],
                "winners": {"protein": {"fdc_id": 2012128, "value": 12.5, "criterion": "highest"}},
            }
        ),
    )


def _recipe_discovery() -> dict:
    return declare_discovery_extension(
        input={"ingredients": [{"fdc_id": 2012128, "grams": 100.0}]},
        input_schema={
            "type": "object",
            "properties": {
                "ingredients": {
                    "type": "array",
                    "minItems": 1,
                    "items": {
                        "type": "object",
                        "properties": {
                            "fdc_id": {"type": "integer"},
                            "grams": {"type": "number", "exclusiveMinimum": 0},
                        },
                        "required": ["fdc_id", "grams"],
                    },
                }
            },
            "required": ["ingredients"],
        },
        body_type="json",
        output=OutputConfig(
            example={
                "total_grams": 100,
                "ingredient_count": 1,
                "nutrition": {"calories": 312.0, "protein": 12.5},
            }
        ),
    )


@router.get("/.well-known/x402", include_in_schema=False)
async def well_known_x402() -> dict:
    return {
        "x402Version": 2,
        "service": {
            "name": "NutriRef",
            "description": (
                "USDA FoodData Central nutrition data, gated by x402 micropayments. "
                "Returns normalized nutrition per 100g across 13 tracked nutrients. "
                "No signup, no API keys."
            ),
            "url": _BASE_URL,
            "openapi": _BASE_URL + "/openapi.json",
            "docs": _BASE_URL + "/docs",
            "mcp": "python -m mcp_server (see https://github.com/Younghef/nutriref-api)",
        },
        "resources": [
            _resource(
                "GET",
                "/v1/nutrition/search?q={query}&limit={n}",
                "0.001",
                "Search USDA foods by name; returns ranked matches with fdc_id and macros.",
                _search_discovery(),
            ),
            _resource(
                "GET",
                "/v1/nutrition/detail/{fdc_id}",
                "0.002",
                "Full normalized nutrition for one food (13 nutrients per 100g).",
                _detail_discovery(),
            ),
            _resource(
                "POST",
                "/v1/nutrition/compare",
                "0.003",
                "Compare 2-5 foods side by side with per-nutrient winners.",
                _compare_discovery(),
            ),
            _resource(
                "POST",
                "/v1/nutrition/recipe",
                "0.005",
                "Scale and sum nutrition across recipe ingredients.",
                _recipe_discovery(),
            ),
        ],
    }


_LLMS_TXT = f"""# NutriRef

> Pay-per-call USDA nutrition data for AI agents. Each request charges
> $0.001-$0.005 in USDC on Base mainnet via the x402 micropayment protocol.
> No signup, no API keys, no human auth flows.

## How to call it

Unpaid requests return HTTP 402 with payment instructions. Any x402-aware
HTTP client (e.g. the `x402` Python package) signs a gasless USDC
authorization (EIP-3009) and retries. Most LLM agents will want the MCP
server wrapper described below; humans wiring a script can also call the
HTTP API directly.

## Endpoints

- GET  /v1/nutrition/search?q={{query}}&limit={{n}}  -- $0.001 -- Search USDA foods by name; returns ranked matches with fdc_id, description, brand_owner, and macros.
- GET  /v1/nutrition/detail/{{fdc_id}}              -- $0.002 -- Full normalized nutrition (13 nutrients per 100g) for one food.
- POST /v1/nutrition/compare                        -- $0.003 -- Body: {{"fdc_ids":[id,...]}} (2-5 ids). Returns each food plus per-nutrient winners.
- POST /v1/nutrition/recipe                         -- $0.005 -- Body: {{"ingredients":[{{"fdc_id":id,"grams":g}},...]}}. Returns aggregate nutrition.

## Machine-readable

- OpenAPI: {_BASE_URL}/openapi.json
- Swagger: {_BASE_URL}/docs
- x402 Bazaar discovery: {_BASE_URL}/.well-known/x402
- AI plugin manifest: {_BASE_URL}/.well-known/ai-plugin.json

## MCP

The repo at https://github.com/Younghef/nutriref-api ships an MCP server
that exposes the four endpoints as native agent tools. Install and add
to a MCP client config:

    git clone https://github.com/Younghef/nutriref-api.git
    cd nutriref-api && pip install -e ".[mcp]"
    # then in your MCP client config:
    {{
      "mcpServers": {{
        "nutriref": {{
          "command": "python",
          "args": ["-m", "mcp_server"],
          "env": {{
            "PAYER_PRIVATE_KEY": "0x...funded-wallet-key...",
            "NUTRIREF_BASE_URL": "{_BASE_URL}"
          }}
        }}
      }}
    }}

## Payment details

- Network: Base mainnet (chain id 8453)
- Asset: USDC at {_USDC_BASE_MAINNET}
- Receiver: {settings.x402_receiver_address}
- Settlement: Coinbase CDP facilitator via the x402 protocol; payer wallets
  only need USDC, no native gas (EIP-3009 gasless authorizations).

## Nutrients tracked per /detail response

Per 100g: calories, protein, fat, carbs, fiber, sugar, sodium, cholesterol,
saturated_fat, vitamin_c, calcium, iron, potassium. Missing nutrients are
null, not zero.
"""


@router.get("/llms.txt", include_in_schema=False, response_class=PlainTextResponse)
async def llms_txt() -> str:
    return _LLMS_TXT


_LOGO_SVG = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" role="img" aria-label="NutriRef">
  <rect width="256" height="256" rx="48" fill="#0a6e3a"/>
  <text x="50%" y="55%" text-anchor="middle" dominant-baseline="middle"
        font-family="-apple-system,Segoe UI,Roboto,sans-serif" font-weight="700"
        font-size="120" fill="#fafaf7">NR</text>
</svg>
"""


@router.get("/logo.svg", include_in_schema=False)
async def logo_svg() -> Response:
    return Response(content=_LOGO_SVG, media_type="image/svg+xml")


@router.get("/.well-known/ai-plugin.json", include_in_schema=False)
async def ai_plugin_manifest() -> dict:
    return {
        "schema_version": "v1",
        "name_for_human": "NutriRef",
        "name_for_model": "nutriref",
        "description_for_human": "Pay-per-call USDA nutrition data for AI agents.",
        "description_for_model": (
            "Look up structured USDA FoodData Central nutrition for any food. "
            "Each call charges a small amount of USDC ($0.001-$0.005) on Base "
            "mainnet via the x402 micropayment protocol — no signup, no API "
            "keys. Use search to find an fdc_id, then detail for full per-100g "
            "nutrition (13 nutrients). Use compare for side-by-side macros and "
            "winners, recipe to scale and sum nutrition across ingredients."
        ),
        "auth": {"type": "none"},
        "api": {"type": "openapi", "url": f"{_BASE_URL}/openapi.json"},
        "logo_url": f"{_BASE_URL}/logo.svg",
        "contact_email": "noreply@nutriref.xyz",
        "legal_info_url": _BASE_URL,
    }
