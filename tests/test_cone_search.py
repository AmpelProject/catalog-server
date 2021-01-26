import pytest

from app.cone_search import (
    CatsHTMQueryItem,
    ConeSearchRequest,
    ExtcatsQueryItem,
)

request = ConeSearchRequest(
    ra_deg=0.5,
    dec_deg=0.5,
    catalogs=[
        CatsHTMQueryItem(**{"name": "GAIADR2", "rs_arcsec": 60}),
        ExtcatsQueryItem(**{"name": "milliquas", "rs_arcsec": 60}),
    ],
)

@pytest.mark.parametrize("ra,dec,catalogs,expected", [
    (5,5,[CatsHTMQueryItem(**{"name": "ROSATfsc", "rs_arcsec": 3600})], [True]),
    (5,5,[CatsHTMQueryItem(**{"name": "ROSATfsc", "rs_arcsec": 60})], [False]),
    (5,5,[ExtcatsQueryItem(**{"name": "milliquas", "rs_arcsec": 60})], [False]),
    (265,-89.58,[ExtcatsQueryItem(**{"name": "milliquas", "rs_arcsec": 60})], [True]),
])
@pytest.mark.asyncio
async def test_search_any(ra, dec, catalogs, expected, test_client):
    request = ConeSearchRequest(
        ra_deg=ra, dec_deg=dec, catalogs=catalogs
    )
    response = await test_client.post("/cone_search/any", json=request.dict())
    response.raise_for_status()
    assert response.json() == expected

@pytest.mark.parametrize("ra,dec,catalogs,expected", [
    (5,5,[CatsHTMQueryItem(**{"name": "ROSATfsc", "rs_arcsec": 3600})], [True]),
    (5,5,[CatsHTMQueryItem(**{"name": "ROSATfsc", "rs_arcsec": 60})], [None]),
    (5,5,[ExtcatsQueryItem(**{"name": "milliquas", "rs_arcsec": 60})], [None]),
    (265,-89.58,[ExtcatsQueryItem(**{"name": "milliquas", "rs_arcsec": 60})], [True]),
])
@pytest.mark.asyncio
async def test_search_nearest(ra, dec, catalogs, expected, test_client):
    request = ConeSearchRequest(
        ra_deg=ra, dec_deg=dec, catalogs=catalogs
    )
    response = await test_client.post("/cone_search/nearest", json=request.dict())
    response.raise_for_status()
    assert len(body := response.json()) == 1
    if expected[0]:
        assert body[0]["dist_arcsec"] < catalogs[0].rs_arcsec
    else:
        assert body == expected

@pytest.mark.parametrize("ra,dec,catalogs,expected", [
    (5,5,[CatsHTMQueryItem(**{"name": "ROSATfsc", "rs_arcsec": 3600})], 9),
    (5,5,[CatsHTMQueryItem(**{"name": "ROSATfsc", "rs_arcsec": 60})], None),
    (5,5,[ExtcatsQueryItem(**{"name": "milliquas", "rs_arcsec": 60})], None),
    (265,-89.58,[ExtcatsQueryItem(**{"name": "milliquas", "rs_arcsec": 60})], 1),
])
async def test_search_all(ra, dec, catalogs, expected, test_client):
    request = ConeSearchRequest(
        ra_deg=ra, dec_deg=dec, catalogs=catalogs
    )
    response = await test_client.post("/cone_search/all", json=request.dict())
    response.raise_for_status()
    assert len(body := response.json()) == 1
    if expected:
        for entry in body[0]:
            assert entry["body"]
    else:
        assert body[0] is None

