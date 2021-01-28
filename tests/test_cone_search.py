import pytest

from app.cone_search import (
    CatsHTMQueryItem,
    ConeSearchRequest,
    ExtcatsQueryItem,
)


@pytest.mark.parametrize("method", ["any", "nearest", "all"])
@pytest.mark.parametrize("use", ["catsHTM", "extcats"])
@pytest.mark.asyncio
async def test_invalid_catalog_name(method, use, test_client):
    """
    Endpoints return meaningful exception if given an invalid catalog name
    """
    # build request explicitly to avoid premature validation
    request = {
        "ra_deg": 0,
        "dec_deg": 0,
        "catalogs": [{"name": "nonesuch", "use": use, "rs_arcsec": 0}],
    }
    response = await test_client.post(f"/cone_search/{method}", json=request)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_missing_keys_doc(without_keys_doc, mock_client):
    """
    Extcats catalogs without ra_key metadata are treated as missing
    """
    # build request explicitly to avoid premature validation
    request = {
        "ra_deg": 0,
        "dec_deg": 0,
        "catalogs": [{"name": "milliquas", "use": "extcats", "rs_arcsec": 0}],
    }
    response = await mock_client.post("/cone_search/nearest", json=request)
    assert response.status_code == 422


def with_request(expected):
    requests = [
        (5, 5, [{"use": "catsHTM", "name": "ROSATfsc", "rs_arcsec": 3600}]),
        (5, 5, [{"use": "catsHTM", "name": "ROSATfsc", "rs_arcsec": 60}]),
        (5, 5, [{"use": "extcats", "name": "milliquas", "rs_arcsec": 60}]),
        (265, -89.58, [{"use": "extcats", "name": "milliquas", "rs_arcsec": 60}],),
    ]
    return pytest.mark.parametrize(
        "request_dict,expected",
        [
            ({"ra_deg": ra, "dec_deg": dec, "catalogs": catalogs}, e)
            for (ra, dec, catalogs), e in zip(requests, expected)
        ],
    )


@with_request([[True], [False], [False], [True]])
@pytest.mark.asyncio
async def test_search_any(request_dict, expected, test_client):
    response = await test_client.post("/cone_search/any", json=request_dict)
    response.raise_for_status()
    assert response.json() == expected


@with_request([[True], [None], [None], [True]])
@pytest.mark.asyncio
async def test_search_nearest(request_dict, expected, test_client):
    response = await test_client.post("/cone_search/nearest", json=request_dict)
    response.raise_for_status()
    body = response.json()
    assert len(body) == 1
    if expected[0]:
        assert body[0]["dist_arcsec"] < request_dict["catalogs"][0]["rs_arcsec"]
    else:
        assert body == expected


@with_request([9, None, None, 1])
@pytest.mark.asyncio
async def test_search_all(request_dict, expected, test_client):
    response = await test_client.post("/cone_search/all", json=request_dict)
    response.raise_for_status()
    body = response.json()
    assert len(body) == 1
    if expected:
        for entry in body[0]:
            assert entry["body"]
    else:
        assert body[0] is None
