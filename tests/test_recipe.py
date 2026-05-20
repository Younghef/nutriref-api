import httpx
import respx

from app import usda
from app.routes.recipe import recipe
from app.schemas import RecipeIngredient, RecipeRequest
from tests.fixtures import food_payload


@respx.mock
async def test_recipe_scales_and_sums_by_grams():
    usda._client = httpx.AsyncClient(base_url="https://api.nal.usda.gov/fdc/v1")

    # Food 1: 100 cal, 10g protein per 100g
    respx.get("https://api.nal.usda.gov/fdc/v1/food/1").mock(
        return_value=httpx.Response(200, json=food_payload(1, "A", {"208": 100.0, "203": 10.0}))
    )
    # Food 2: 200 cal, 20g protein per 100g
    respx.get("https://api.nal.usda.gov/fdc/v1/food/2").mock(
        return_value=httpx.Response(200, json=food_payload(2, "B", {"208": 200.0, "203": 20.0}))
    )

    result = await recipe(
        RecipeRequest(
            ingredients=[
                RecipeIngredient(fdc_id=1, grams=200),  # 200 cal, 20g protein
                RecipeIngredient(fdc_id=2, grams=50),   # 100 cal, 10g protein
            ]
        )
    )

    assert result.total_grams == 250
    assert result.ingredient_count == 2
    assert result.nutrition["calories"] == 300.0
    assert result.nutrition["protein"] == 30.0
    assert result.nutrition["fiber"] is None  # neither food had fiber


@respx.mock
async def test_recipe_single_ingredient_half_serving():
    usda._client = httpx.AsyncClient(base_url="https://api.nal.usda.gov/fdc/v1")

    respx.get("https://api.nal.usda.gov/fdc/v1/food/9").mock(
        return_value=httpx.Response(200, json=food_payload(9, "X", {"208": 80.0, "205": 20.0}))
    )

    result = await recipe(RecipeRequest(ingredients=[RecipeIngredient(fdc_id=9, grams=50)]))

    assert result.total_grams == 50
    assert result.nutrition["calories"] == 40.0
    assert result.nutrition["carbs"] == 10.0
