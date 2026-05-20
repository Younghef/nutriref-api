from app.normalize import NUTRIENT_FIELDS, normalize_food, normalize_search_hit
from tests.fixtures import food_payload, search_hit


def test_normalize_food_flattens_nutrients():
    payload = food_payload(
        123,
        "Banana, raw",
        {"208": 89.0, "203": 1.1, "204": 0.3, "205": 22.8, "291": 2.6, "306": 358.0},
    )
    result = normalize_food(payload)
    assert result["fdc_id"] == 123
    assert result["description"] == "Banana, raw"
    assert result["calories"] == 89.0
    assert result["protein"] == 1.1
    assert result["potassium"] == 358.0


def test_normalize_food_missing_nutrient_is_none_not_zero():
    payload = food_payload(99, "Sparse Food", {"208": 50.0})
    result = normalize_food(payload)
    assert result["calories"] == 50.0
    assert result["protein"] is None
    assert result["sodium"] is None


def test_normalize_food_returns_all_thirteen_nutrient_fields():
    result = normalize_food(food_payload(1, "x", {}))
    for field in NUTRIENT_FIELDS:
        assert field in result


def test_normalize_search_hit_lightweight_subset():
    hit = search_hit(7, "Apple", {"208": 52.0, "203": 0.3, "204": 0.2, "205": 14.0, "306": 107.0})
    result = normalize_search_hit(hit)
    assert set(result.keys()) == {
        "fdc_id", "description", "brand_owner", "calories", "protein", "carbs", "fat"
    }
    assert result["calories"] == 52.0
    assert "potassium" not in result
