import httpx
import respx

from app import usda
from app.routes.detail import detail
from tests.fixtures import food_payload


@respx.mock
async def test_detail_caches_on_second_call():
    usda._client = httpx.AsyncClient(base_url="https://api.nal.usda.gov/fdc/v1")

    route = respx.get("https://api.nal.usda.gov/fdc/v1/food/123").mock(
        return_value=httpx.Response(
            200,
            json=food_payload(
                123,
                "Banana, raw",
                {"208": 89.0, "203": 1.1, "204": 0.3, "205": 22.8, "291": 2.6, "306": 358.0},
            ),
        )
    )

    first = await detail(fdc_id=123)
    second = await detail(fdc_id=123)

    assert route.call_count == 1
    assert first.fdc_id == 123
    assert first.calories == 89.0
    assert first.potassium == 358.0
    assert second.fdc_id == first.fdc_id
