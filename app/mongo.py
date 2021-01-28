from functools import lru_cache

from extcats.CatalogQuery import CatalogQuery
from pymongo import MongoClient

from .settings import settings

mongo_db = MongoClient(settings.mongo_uri)


def get_mongo() -> MongoClient:
    return mongo_db


@lru_cache(maxsize=128)
def get_catq(name: str) -> CatalogQuery:
    return CatalogQuery(name, dbclient=get_mongo())
