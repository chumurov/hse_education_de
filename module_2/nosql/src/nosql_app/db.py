from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from pymongo import MongoClient
from pymongo.database import Database

from nosql_app.config import get_settings


def create_client(mongo_uri: str | None = None) -> MongoClient:
    settings = get_settings()
    return MongoClient(mongo_uri or settings.mongo_uri, serverSelectionTimeoutMS=3000)


@contextmanager
def mongo_database(mongo_uri: str | None = None, db_name: str | None = None) -> Iterator[Database]:
    settings = get_settings()
    client = create_client(mongo_uri or settings.mongo_uri)
    try:
        database = client[db_name or settings.db_name]
        client.admin.command("ping")
        yield database
    finally:
        client.close()


def ping(mongo_uri: str | None = None) -> dict:
    with mongo_database(mongo_uri=mongo_uri) as database:
        return database.client.admin.command("ping")

