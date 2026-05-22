from fastapi import APIRouter, Query
from fastapi_x402 import pay

from app import usda
from app.cache import get_json, make_key, set_json
from app.normalize import normalize_search_hit
from app.schemas import SearchHit, SearchResponse

router = APIRouter()

SEARCH_TTL = 24 * 60 * 60  # 24 hours


@router.get(
    "/search",
    response_model=SearchResponse,
    summary="Search USDA foods by name",
    description=(
        "Searches USDA FoodData Central for foods matching `q`. Returns ranked matches with "
        "their `fdc_id` plus a lightweight macro summary (calories, protein, carbs, fat). "
        "Use the returned `fdc_id` with /detail for the full nutrient breakdown. "
        "**Price: $0.001 per request.** Cached 24h."
    ),
    response_description="Up to `limit` ranked food matches with fdc_id and macros.",
)
@pay("$0.001")
async def search(
    q: str = Query(..., min_length=1, description="Free-text food name to search (e.g. \"banana\", \"greek yogurt\")."),
    limit: int = Query(10, ge=1, le=50, description="Max number of results to return (1–50)."),
) -> SearchResponse:
    key = make_key("search", q.lower(), limit)
    cached = await get_json(key)
    if cached is not None:
        return SearchResponse(**cached)

    raw = await usda.search_foods(q, limit)
    hits = [normalize_search_hit(h) for h in raw.get("foods", [])]
    payload = SearchResponse(
        query=q,
        count=len(hits),
        results=[SearchHit(**h) for h in hits],
    )
    await set_json(key, payload.model_dump(), SEARCH_TTL)
    return payload
