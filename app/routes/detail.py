from fastapi import APIRouter
from fastapi_x402 import pay

from app.schemas import NormalizedFood
from app.services import get_detail_cached

router = APIRouter()


@router.get(
    "/detail/{fdc_id}",
    response_model=NormalizedFood,
    summary="Full nutrition for one food by FDC ID",
    description=(
        "Returns the full normalized nutrition record for a USDA FoodData Central food, "
        "by `fdc_id`. All 13 tracked nutrients are returned per 100g; missing values are `null` "
        "rather than 0. Get the `fdc_id` from /search first. "
        "**Price: $0.002 per request.** Cached 7d."
    ),
    response_description="Normalized food with 13 nutrient fields per 100g.",
)
@pay("$0.002")
async def detail(fdc_id: int) -> NormalizedFood:
    food = await get_detail_cached(fdc_id)
    return NormalizedFood(**food)
