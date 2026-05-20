import asyncio

from fastapi import APIRouter
from fastapi_x402 import pay

from app.normalize import NUTRIENT_FIELDS
from app.schemas import RecipeRequest, RecipeResponse
from app.services import get_detail_cached

router = APIRouter()


@router.post("/recipe", response_model=RecipeResponse)
@pay("$0.005")
async def recipe(req: RecipeRequest) -> RecipeResponse:
    foods = await asyncio.gather(*(get_detail_cached(i.fdc_id) for i in req.ingredients))

    totals: dict[str, float | None] = {field: None for field in NUTRIENT_FIELDS}

    for ingredient, food in zip(req.ingredients, foods):
        scale = ingredient.grams / 100.0
        for field in NUTRIENT_FIELDS:
            value = food.get(field)
            if value is None:
                continue
            scaled = value * scale
            totals[field] = scaled if totals[field] is None else totals[field] + scaled

    return RecipeResponse(
        total_grams=sum(i.grams for i in req.ingredients),
        ingredient_count=len(req.ingredients),
        nutrition=totals,
    )
