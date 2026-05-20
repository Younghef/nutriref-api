import httpx
from fastapi import HTTPException

from app.config import settings


_client: httpx.AsyncClient | None = None


def get_client() -> httpx.AsyncClient:
    global _client
    if _client is None:
        _client = httpx.AsyncClient(timeout=10.0, base_url=settings.usda_base_url)
    return _client


async def close_client() -> None:
    global _client
    if _client is not None:
        await _client.aclose()
        _client = None


def _handle_status(resp: httpx.Response) -> None:
    if resp.status_code == 404:
        raise HTTPException(status_code=404, detail="Food not found in USDA FoodData Central")
    if resp.status_code == 429:
        raise HTTPException(
            status_code=503,
            detail="USDA upstream rate limit hit; retry shortly",
            headers={"Retry-After": "30"},
        )
    if resp.status_code >= 500:
        raise HTTPException(status_code=502, detail="USDA upstream error")
    resp.raise_for_status()


async def search_foods(query: str, limit: int) -> dict:
    resp = await get_client().get(
        "/foods/search",
        params={"query": query, "pageSize": limit, "api_key": settings.usda_api_key},
    )
    _handle_status(resp)
    return resp.json()


async def get_food(fdc_id: int) -> dict:
    resp = await get_client().get(
        f"/food/{fdc_id}",
        params={"api_key": settings.usda_api_key},
    )
    _handle_status(resp)
    return resp.json()
