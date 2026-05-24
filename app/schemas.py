from pydantic import BaseModel, ConfigDict, Field, conlist


class NormalizedFood(BaseModel):
    """Flat per-100g nutrition for one food. Missing nutrients are null, not 0."""

    fdc_id: int
    description: str | None = None
    brand_owner: str | None = None
    data_type: str | None = None
    serving_size: float | None = None
    serving_size_unit: str | None = None

    calories: float | None = None
    protein: float | None = None
    fat: float | None = None
    carbs: float | None = None
    fiber: float | None = None
    sugar: float | None = None
    sodium: float | None = None
    cholesterol: float | None = None
    saturated_fat: float | None = None
    vitamin_c: float | None = None
    calcium: float | None = None
    iron: float | None = None
    potassium: float | None = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "fdc_id": 173944,
                "description": "Banana, raw",
                "brand_owner": None,
                "data_type": "Foundation",
                "serving_size": 100,
                "serving_size_unit": "g",
                "calories": 89.0,
                "protein": 1.1,
                "fat": 0.3,
                "carbs": 22.8,
                "fiber": 2.6,
                "sugar": 12.2,
                "sodium": 1.0,
                "cholesterol": None,
                "saturated_fat": 0.1,
                "vitamin_c": 8.7,
                "calcium": 5.0,
                "iron": 0.3,
                "potassium": 358.0,
            }
        }
    )


class SearchHit(BaseModel):
    """Lightweight subset used in search responses."""

    fdc_id: int
    description: str | None = None
    brand_owner: str | None = None
    calories: float | None = None
    protein: float | None = None
    carbs: float | None = None
    fat: float | None = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "fdc_id": 2012128,
                "description": "BANANA",
                "brand_owner": "Wonder Natural Foods Corp",
                "calories": 312.0,
                "protein": 12.5,
                "carbs": 40.62,
                "fat": 6.25,
            }
        }
    )


class SearchResponse(BaseModel):
    query: str
    count: int
    results: list[SearchHit]

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "query": "banana",
                "count": 2,
                "results": [
                    {
                        "fdc_id": 2012128,
                        "description": "BANANA",
                        "brand_owner": "Wonder Natural Foods Corp",
                        "calories": 312.0,
                        "protein": 12.5,
                        "carbs": 40.62,
                        "fat": 6.25,
                    },
                    {
                        "fdc_id": 173944,
                        "description": "Banana, raw",
                        "brand_owner": None,
                        "calories": 89.0,
                        "protein": 1.1,
                        "carbs": 22.8,
                        "fat": 0.3,
                    },
                ],
            }
        }
    )


class CompareRequest(BaseModel):
    fdc_ids: conlist(int, min_length=2, max_length=5)

    model_config = ConfigDict(
        json_schema_extra={"example": {"fdc_ids": [2012128, 173944]}}
    )


class Winner(BaseModel):
    fdc_id: int
    value: float
    criterion: str = Field(description='Direction the winner was selected by: "highest" or "lowest".')


class CompareResponse(BaseModel):
    foods: list[NormalizedFood]
    winners: dict[str, Winner | dict[str, Winner]]

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "foods": [
                    {"fdc_id": 2012128, "description": "BANANA", "protein": 12.5, "sodium": 594.0, "calories": 312.0},
                    {"fdc_id": 173944, "description": "Banana, raw", "protein": 1.1, "sodium": 1.0, "calories": 89.0},
                ],
                "winners": {
                    "protein": {"fdc_id": 2012128, "value": 12.5, "criterion": "highest"},
                    "sodium": {"fdc_id": 173944, "value": 1.0, "criterion": "lowest"},
                    "calories": {
                        "highest": {"fdc_id": 2012128, "value": 312.0, "criterion": "highest"},
                        "lowest": {"fdc_id": 173944, "value": 89.0, "criterion": "lowest"},
                    },
                },
            }
        }
    )


class RecipeIngredient(BaseModel):
    fdc_id: int
    grams: float = Field(gt=0)

    model_config = ConfigDict(
        json_schema_extra={"example": {"fdc_id": 173944, "grams": 150.0}}
    )


class RecipeRequest(BaseModel):
    ingredients: list[RecipeIngredient] = Field(min_length=1)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "ingredients": [
                    {"fdc_id": 173944, "grams": 150.0},
                    {"fdc_id": 2012128, "grams": 50.0},
                ]
            }
        }
    )


class RecipeResponse(BaseModel):
    total_grams: float
    ingredient_count: int
    nutrition: dict[str, float | None]

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_grams": 200,
                "ingredient_count": 2,
                "nutrition": {
                    "calories": 289.5,
                    "protein": 7.9,
                    "fat": 3.6,
                    "carbs": 54.5,
                    "fiber": 3.9,
                    "sugar": 21.4,
                    "sodium": 298.5,
                    "cholesterol": 0.0,
                    "saturated_fat": 0.15,
                    "vitamin_c": 20.6,
                    "calcium": 70.0,
                    "iron": 1.01,
                    "potassium": 537.0,
                },
            }
        }
    )
