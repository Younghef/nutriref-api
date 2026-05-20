from typing import Any

NUTRIENT_MAP: dict[str, str] = {
    "208": "calories",
    "203": "protein",
    "204": "fat",
    "205": "carbs",
    "291": "fiber",
    "269": "sugar",
    "307": "sodium",
    "601": "cholesterol",
    "606": "saturated_fat",
    "401": "vitamin_c",
    "301": "calcium",
    "303": "iron",
    "306": "potassium",
}

NUTRIENT_FIELDS: tuple[str, ...] = tuple(NUTRIENT_MAP.values())


def _extract_nutrient_number(fn: dict[str, Any]) -> str | None:
    """USDA returns nutrient blocks in two shapes depending on the endpoint."""
    nutrient = fn.get("nutrient")
    if isinstance(nutrient, dict) and "number" in nutrient:
        return str(nutrient["number"])
    if "nutrientNumber" in fn:
        return str(fn["nutrientNumber"])
    return None


def _extract_amount(fn: dict[str, Any]) -> float | None:
    for key in ("amount", "value"):
        if key in fn and fn[key] is not None:
            try:
                return float(fn[key])
            except (TypeError, ValueError):
                return None
    return None


def normalize_food(payload: dict[str, Any]) -> dict[str, Any]:
    """USDA /food/{fdcId} → flat normalized schema. Missing nutrients are None, not 0."""
    nutrients: dict[str, float | None] = {field: None for field in NUTRIENT_FIELDS}

    for fn in payload.get("foodNutrients", []) or []:
        number = _extract_nutrient_number(fn)
        if number is None:
            continue
        field = NUTRIENT_MAP.get(number)
        if field is None:
            continue
        nutrients[field] = _extract_amount(fn)

    return {
        "fdc_id": payload.get("fdcId"),
        "description": payload.get("description"),
        "brand_owner": payload.get("brandOwner"),
        "data_type": payload.get("dataType"),
        "serving_size": payload.get("servingSize"),
        "serving_size_unit": payload.get("servingSizeUnit"),
        **nutrients,
    }


def normalize_search_hit(hit: dict[str, Any]) -> dict[str, Any]:
    """Lightweight subset for /search responses."""
    full = normalize_food(hit)
    return {
        "fdc_id": full["fdc_id"],
        "description": full["description"],
        "brand_owner": full["brand_owner"],
        "calories": full["calories"],
        "protein": full["protein"],
        "carbs": full["carbs"],
        "fat": full["fat"],
    }
