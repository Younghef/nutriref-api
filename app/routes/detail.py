from fastapi import APIRouter
from fastapi_x402 import pay

from app.schemas import NormalizedFood
from app.services import get_detail_cached

router = APIRouter()


@router.get("/detail/{fdc_id}", response_model=NormalizedFood)
@pay("$0.002")
async def detail(fdc_id: int) -> NormalizedFood:
    food = await get_detail_cached(fdc_id)
    return NormalizedFood(**food)
