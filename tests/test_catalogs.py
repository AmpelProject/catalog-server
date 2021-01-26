
import pytest

@pytest.mark.asyncio
async def test_list_catalogs(test_client):
    response = await test_client.get("/catalogs")
    response.raise_for_status()
    assert isinstance(body := response.json(), list)
    assert len(body) == 2
    assert (extcats := body[0])["use"] == "extcats"
    assert extcats["name"] == "milliquas"
    assert len(extcats["columns"]) == 21

    assert (catshtm := body[1])["use"] == "catsHTM"
    assert len(catshtm["columns"]) == 21
