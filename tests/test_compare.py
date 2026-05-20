import httpx
import respx

from app import usda
from app.routes.compare import compare
from app.schemas import CompareRequest
from tests.fixtures import food_payload


@respx.mock
async def test_compare_picks_winners_by_direction():
    usda._client = httpx.AsyncClient(base_url="https://api.nal.usda.gov/fdc/v1")

    respx.get("https://api.nal.usda.gov/fdc/v1/food/1").mock(
        return_value=httpx.Response(
            200,
            json=food_payload(
                1,
                "High protein",
                {"203": 25.0, "291": 2.0, "307": 200.0, "208": 300.0},
            ),
        )
    )
    respx.get("https://api.nal.usda.gov/fdc/v1/food/2").mock(
        return_value=httpx.Response(
            200,
            json=food_payload(
                2,
                "High fiber",
                {"203": 5.0, "291": 10.0, "307": 50.0, "208": 150.0},
            ),
        )
    )

    result = await compare(CompareRequest(fdc_ids=[1, 2]))

    # higher-is-better
    assert result.winners["protein"].fdc_id == 1
    assert result.winners["protein"].criterion == "highest"
    assert result.winners["fiber"].fdc_id == 2
    # lower-is-better
    assert result.winners["sodium"].fdc_id == 2
    assert result.winners["sodium"].criterion == "lowest"
    # report-both for calories
    calories = result.winners["calories"]
    assert calories["highest"].fdc_id == 1
    assert calories["lowest"].fdc_id == 2


@respx.mock
async def test_compare_skips_missing_nutrients():
    usda._client = httpx.AsyncClient(base_url="https://api.nal.usda.gov/fdc/v1")

    respx.get("https://api.nal.usda.gov/fdc/v1/food/10").mock(
        return_value=httpx.Response(200, json=food_payload(10, "A", {"203": 5.0}))
    )
    respx.get("https://api.nal.usda.gov/fdc/v1/food/11").mock(
        return_value=httpx.Response(200, json=food_payload(11, "B", {"203": 10.0}))
    )

    result = await compare(CompareRequest(fdc_ids=[10, 11]))
    assert result.winners["protein"].fdc_id == 11
    # No iron data on either → key absent.
    assert "iron" not in result.winners
