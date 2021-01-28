
from typing import Generator
from pymongo import MongoClient
from pymongo.errors import OperationFailure

from .settings import settings

mongo_db = MongoClient(settings.mongo_uri)

def get_mongo() -> Generator[MongoClient, None, None]:
    yield mongo_db
