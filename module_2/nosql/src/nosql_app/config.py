from __future__ import annotations

import os
from dataclasses import dataclass
from urllib.parse import urlparse

from dotenv import load_dotenv


DEFAULT_MONGO_URI = "mongodb://localhost:27018/appdb"
DEFAULT_DB_NAME = "appdb"


@dataclass(frozen=True, slots=True)
class Settings:
    mongo_uri: str
    db_name: str


def _db_name_from_uri(mongo_uri: str) -> str | None:
    path = urlparse(mongo_uri).path.lstrip("/")
    return path or None


def get_settings() -> Settings:
    load_dotenv(override=False)
    mongo_uri = os.getenv("APP_MONGO_URI", DEFAULT_MONGO_URI)
    db_name = os.getenv("APP_MONGO_DB") or _db_name_from_uri(mongo_uri) or DEFAULT_DB_NAME
    return Settings(mongo_uri=mongo_uri, db_name=db_name)

