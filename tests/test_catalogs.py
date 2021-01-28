import pytest


@pytest.mark.asyncio
async def test_list_catalogs(test_client):
    response = await test_client.get("/catalogs")
    response.raise_for_status()
    body = response.json()
    assert isinstance(body, list)
    assert len(body) == 2

    extcats = body[0]
    assert extcats["use"] == "extcats"
    assert extcats["name"] == "milliquas"
    assert len(extcats["columns"]) == 21

    catshtm = body[1]
    assert catshtm["use"] == "catsHTM"
    assert len(catshtm["columns"]) == 21


@pytest.mark.asyncio
async def test_missing_keys_doc(without_keys_doc, mock_client):
    """
    Extcats catalogs without ra_key metadata are treated as missing
    """
    response = await mock_client.get("/catalogs")
    response.raise_for_status()
    body = response.json()
    assert not [c for c in body if c["name"] == "milliquas"]
