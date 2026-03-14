from __future__ import annotations

import json
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from bson import ObjectId
from bson.timestamp import Timestamp


def to_jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: to_jsonable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [to_jsonable(item) for item in value]
    if isinstance(value, tuple):
        return [to_jsonable(item) for item in value]
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, ObjectId):
        return str(value)
    if isinstance(value, Timestamp):
        return {"time": value.time, "inc": value.inc}
    if isinstance(value, bytes):
        return value.hex()
    if isinstance(value, Decimal):
        return float(value)
    return value


def dumps(data: Any) -> str:
    return json.dumps(to_jsonable(data), ensure_ascii=False, indent=2, sort_keys=True)
