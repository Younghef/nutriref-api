import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi_x402 import init_x402
from fastapi_x402 import networks as x402_networks

from app import usda
from app.cache import close_redis
from app.config import settings
from app.routes import compare, detail, recipe, search


logging.basicConfig(level=settings.log_level)

# fastapi-x402 ships the wrong EIP-712 token name for Base mainnet USDC — it uses
# "USDC" where the contract's on-chain domain name is "USD Coin". The payer signs
# transferWithAuthorization against that domain, so a mismatch makes the facilitator's
# verification revert (invalid_payload). Correct it before init_x402 builds challenges.
_base_usdc = x402_networks.NETWORK_CONFIGS["base"].assets["usdc"]
_base_usdc.name = "USD Coin"
_base_usdc.eip712_name = "USD Coin"


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await usda.close_client()
    await close_redis()


app = FastAPI(
    title="NutriRef",
    description="Monetized USDA FoodData Central API for AI agents, gated by x402 micropayments.",
    version="0.1.0",
    lifespan=lifespan,
)

init_x402(
    app,
    pay_to=settings.x402_receiver_address,
    network=settings.x402_network,
    facilitator_url=settings.x402_facilitator_url,
)

app.include_router(search.router, prefix="/v1/nutrition", tags=["nutrition"])
app.include_router(detail.router, prefix="/v1/nutrition", tags=["nutrition"])
app.include_router(compare.router, prefix="/v1/nutrition", tags=["nutrition"])
app.include_router(recipe.router, prefix="/v1/nutrition", tags=["nutrition"])


@app.get("/health", tags=["meta"])
async def health() -> dict[str, str]:
    return {"status": "ok"}
