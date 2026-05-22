import asyncio
from typing import Any

from fastapi import APIRouter
from fastapi_x402 import pay

from app.schemas import CompareRequest, CompareResponse, NormalizedFood, Winner
from app.services import get_detail_cached

router = APIRouter()

# Directional rules per nutrient.
HIGHER_IS_BETTER = {"protein", "fiber", "vitamin_c", "calcium", "iron", "potassium"}
LOWER_IS_BETTER = {"sodium", "sugar", "saturated_fat", "cholesterol"}
REPORT_BOTH = {"calories", "fat", "carbs"}


def _winner(foods: list[dict[str, Any]], field: str, *, highest: bool) -> Winner | None:
    candidates = [(f["fdc_id"], f[field]) for f in foods if f.get(field) is not None]
    if not candidates:
        return None
    fdc_id, value = (max if highest else min)(candidates, key=lambda x: x[1])
    return Winner(fdc_id=fdc_id, value=value, criterion="highest" if highest else "lowest")


def _build_winners(foods: list[dict[str, Any]]) -> dict[str, Any]:
    winners: dict[str, Any] = {}
    for field in HIGHER_IS_BETTER:
        w = _winner(foods, field, highest=True)
        if w is not None:
            winners[field] = w
    for field in LOWER_IS_BETTER:
        w = _winner(foods, field, highest=False)
        if w is not None:
            winners[field] = w
    for field in REPORT_BOTH:
        hi = _winner(foods, field, highest=True)
        lo = _winner(foods, field, highest=False)
        pair: dict[str, Winner] = {}
        if hi is not None:
            pair["highest"] = hi
        if lo is not None:
            pair["lowest"] = lo
        if pair:
            winners[field] = pair
    return winners


@router.post(
    "/compare",
    response_model=CompareResponse,
    summary="Compare 2–5 foods side by side",
    description=(
        "Fetches normalized nutrition for each `fdc_id` and computes per-nutrient winners. "
        "Higher-is-better fields (protein, fiber, vitamin C, calcium, iron, potassium) report the "
        "highest; lower-is-better fields (sodium, sugar, saturated_fat, cholesterol) report the "
        "lowest; calories/fat/carbs report both extremes. Composes from cached /detail calls. "
        "**Price: $0.003 per request.**"
    ),
    response_description="Foods array + per-nutrient winners (with criterion).",
)
@pay("$0.003")
async def compare(req: CompareRequest) -> CompareResponse:
    foods = await asyncio.gather(*(get_detail_cached(fid) for fid in req.fdc_ids))
    return CompareResponse(
        foods=[NormalizedFood(**f) for f in foods],
        winners=_build_winners(foods),
    )
