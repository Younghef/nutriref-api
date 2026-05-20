from app import usda
from app.cache import get_json, make_key, set_json
from app.normalize import normalize_food

DETAIL_TTL = 7 * 24 * 60 * 60  # 7 days


async def get_detail_cached(fdc_id: int) -> dict:
    """Shared helper for /detail, /compare, /recipe. Single source of truth for caching."""
    key = make_key("detail", fdc_id)
    cached = await get_json(key)
    if cached is not None:
        return cached

    raw = await usda.get_food(fdc_id)
    normalized = normalize_food(raw)
    await set_json(key, normalized, DETAIL_TTL)
    return normalized
