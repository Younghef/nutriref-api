import httpx
import respx

from app import usda
from app.routes.search import search
from tests.fixtures import search_hit, search_payload


@respx.mock
async def test_search_caches_on_second_call():
    usda._client = httpx.AsyncClient(base_url="https://api.nal.usda.gov/fdc/v1")

    route = respx.get("https://api.nal.usda.gov/fdc/v1/foods/search").mock(
        return_value=httpx.Response(
            200,
            json=search_payload(
                "banana",
                [search_hit(123, "Banana, raw", {"208": 89.0, "203": 1.1, "204": 0.3, "205": 22.8})],
            ),
        )
    )

    first = await search(q="banana", limit=10)
    second = await search(q="banana", limit=10)

    assert route.call_count == 1
    assert first.count == 1 and second.count == 1
    assert first.results[0].fdc_id == 123
    assert first.results[0].calories == 89.0


@respx.mock
async def test_search_normalizes_hits_to_lightweight_subset():
    usda._client = httpx.AsyncClient(base_url="https://api.nal.usda.gov/fdc/v1")

    respx.get("https://api.nal.usda.gov/fdc/v1/foods/search").mock(
        return_value=httpx.Response(
            200,
            json=search_payload(
                "apple",
                [search_hit(7, "Apple", {"208": 52.0, "203": 0.3, "204": 0.2, "205": 14.0})],
            ),
        )
    )

    result = await search(q="apple", limit=5)
    hit = result.results[0]
    assert hit.protein == 0.3
    assert hit.carbs == 14.0
