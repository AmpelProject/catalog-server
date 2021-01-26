from pathlib import Path

import mongomock
import pytest
from bson import decode_all
from httpx import AsyncClient

from app.main import app
from app.settings import Settings


@pytest.fixture(scope="session")
def mock_mongoclient():
    test_data_dir = Path(__file__).parent / "test-data"
    mc = mongomock.MongoClient()
    # read catalogs from test-data, adding key metadata
    # milliquas happens to have both geoJSON and healpix indexes, and will
    # default to healpix, which works with mongomock
    for catalog in ("milliquas",):
        db = mc.get_database(catalog)
        with open(test_data_dir / "minimongodumps" / catalog / "meta.bson", "rb") as f:
            db.get_collection("meta").insert_many(
                decode_all(f.read()) + [{"_id": "keys", "ra": "ra", "dec": "dec",}]
            )
        with open(test_data_dir / "minimongodumps" / catalog / "srcs.bson", "rb") as f:
            db.get_collection("srcs").insert_many(decode_all(f.read()))
        assert db.get_collection("srcs").count() == 10
    return mc


@pytest.fixture
def mock_extcats(monkeypatch, mock_mongoclient):

    monkeypatch.setattr("app.mongo.mongo_db", mock_mongoclient)
    # replace filter with nothing
    # (mongomock supports neither $geoNear nor $where)
    # FIXME: disable only for geoJSON queries
    # monkeypatch.setattr("extcats.catquery_utils.filters_logical_and", lambda *args: {})


@pytest.fixture
def mock_catshtm(monkeypatch):
    settings = Settings(catshtm_dir=Path(__file__).parent / "test-data" / "catsHTM2")
    monkeypatch.setattr(
        "app.cone_search.settings", settings,
    )
    monkeypatch.setattr(
        "app.catalogs.settings", settings,
    )


@pytest.fixture
async def test_client(mock_extcats, mock_catshtm):
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
