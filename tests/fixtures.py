"""Shared USDA-shaped JSON fixtures for tests."""


def food_payload(fdc_id: int, description: str, nutrients: dict[str, float | None]) -> dict:
    """Build a USDA /food/{fdcId}-shaped payload.

    `nutrients` keys are USDA nutrient numbers as strings (e.g. "203" = protein).
    """
    return {
        "fdcId": fdc_id,
        "description": description,
        "brandOwner": None,
        "dataType": "Foundation",
        "servingSize": 100,
        "servingSizeUnit": "g",
        "foodNutrients": [
            {"nutrient": {"number": number}, "amount": amount}
            for number, amount in nutrients.items()
            if amount is not None
        ],
    }


def search_payload(query: str, hits: list[dict]) -> dict:
    return {
        "totalHits": len(hits),
        "currentPage": 1,
        "foods": hits,
    }


def search_hit(fdc_id: int, description: str, nutrients: dict[str, float | None]) -> dict:
    """Search results use `nutrientNumber` flat keys, not nested `nutrient` blocks."""
    return {
        "fdcId": fdc_id,
        "description": description,
        "brandOwner": None,
        "foodNutrients": [
            {"nutrientNumber": number, "value": amount}
            for number, amount in nutrients.items()
            if amount is not None
        ],
    }
