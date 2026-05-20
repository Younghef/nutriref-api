from pydantic import BaseModel, Field, conlist


class NormalizedFood(BaseModel):
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


class SearchHit(BaseModel):
    fdc_id: int
    description: str | None = None
    brand_owner: str | None = None
    calories: float | None = None
    protein: float | None = None
    carbs: float | None = None
    fat: float | None = None


class SearchResponse(BaseModel):
    query: str
    count: int
    results: list[SearchHit]


class CompareRequest(BaseModel):
    fdc_ids: conlist(int, min_length=2, max_length=5)


class Winner(BaseModel):
    fdc_id: int
    value: float
    criterion: str  # "highest" | "lowest"


class CompareResponse(BaseModel):
    foods: list[NormalizedFood]
    winners: dict[str, Winner | dict[str, Winner]]


class RecipeIngredient(BaseModel):
    fdc_id: int
    grams: float = Field(gt=0)


class RecipeRequest(BaseModel):
    ingredients: list[RecipeIngredient] = Field(min_length=1)


class RecipeResponse(BaseModel):
    total_grams: float
    ingredient_count: int
    nutrition: dict[str, float | None]
