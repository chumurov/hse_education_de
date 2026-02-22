from __future__ import annotations

import os
from datetime import datetime

from pymongo import MongoClient
from pymongo.errors import OperationFailure


DEFAULT_HOST = os.getenv("MONGO_HOST", "localhost")
DEFAULT_PORT = os.getenv("MONGO_PORT", "27017")
DB_NAME = os.getenv("MONGO_DB", "dz_3_itog")


def iso_dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def seed_user_sessions(db) -> None:
    collection = db["UserSessions"]
    documents = [
        {
            "session_id": "sess_001",
            "user_id": "user_123",
            "start_time": iso_dt("2024-01-10T09:00:00Z"),
            "end_time": iso_dt("2024-01-10T09:30:00Z"),
            "pages_visited": ["/home", "/products", "/products/42", "/cart"],
            "device": {"type": "mobile", "os": "Android", "browser": "Chrome"},
            "actions": ["login", "view_product", "add_to_cart", "logout"],
        },
        {
            "session_id": "sess_002",
            "user_id": "user_456",
            "start_time": iso_dt("2024-01-10T10:05:00Z"),
            "end_time": iso_dt("2024-01-10T10:52:00Z"),
            "pages_visited": ["/home", "/search", "/products/101", "/checkout"],
            "device": {"type": "desktop", "os": "Windows", "browser": "Firefox"},
            "actions": ["login", "search", "view_product", "checkout"],
        },
    ]

    for doc in documents:
        collection.update_one(
            {"session_id": doc["session_id"]},
            {"$set": doc},
            upsert=True,
        )


def seed_event_logs(db) -> None:
    collection = db["EventLogs"]
    documents = [
        {
            "event_id": "evt_1001",
            "timestamp": iso_dt("2024-01-10T09:05:20Z"),
            "event_type": "click",
            "details": {"page": "/products/42", "target": "buy_button"},
        },
        {
            "event_id": "evt_1002",
            "timestamp": iso_dt("2024-01-10T09:06:10Z"),
            "event_type": "scroll",
            "details": {"page": "/products/42", "depth_percent": 75},
        },
        {
            "event_id": "evt_1003",
            "timestamp": iso_dt("2024-01-10T10:15:44Z"),
            "event_type": "search",
            "details": {"query": "wireless headphones", "results_count": 24},
        },
    ]

    for doc in documents:
        collection.update_one(
            {"event_id": doc["event_id"]},
            {"$set": doc},
            upsert=True,
        )


def seed_support_tickets(db) -> None:
    collection = db["SupportTickets"]
    documents = [
        {
            "ticket_id": "ticket_789",
            "user_id": "user_123",
            "status": "open",
            "issue_type": "payment",
            "messages": [
                {
                    "sender": "user",
                    "message": "Не могу оплатить заказ.",
                    "timestamp": iso_dt("2024-01-09T12:00:00Z"),
                },
                {
                    "sender": "support",
                    "message": "Пожалуйста, уточните способ оплаты.",
                    "timestamp": iso_dt("2024-01-09T13:00:00Z"),
                },
            ],
            "created_at": iso_dt("2024-01-09T11:55:00Z"),
            "updated_at": iso_dt("2024-01-09T13:00:00Z"),
        },
        {
            "ticket_id": "ticket_790",
            "user_id": "user_456",
            "status": "closed",
            "issue_type": "delivery",
            "messages": [
                {
                    "sender": "user",
                    "message": "Где мой заказ?",
                    "timestamp": iso_dt("2024-01-08T09:10:00Z"),
                },
                {
                    "sender": "support",
                    "message": "Заказ уже передан в службу доставки.",
                    "timestamp": iso_dt("2024-01-08T09:25:00Z"),
                },
            ],
            "created_at": iso_dt("2024-01-08T09:05:00Z"),
            "updated_at": iso_dt("2024-01-08T09:25:00Z"),
        },
    ]

    for doc in documents:
        collection.update_one(
            {"ticket_id": doc["ticket_id"]},
            {"$set": doc},
            upsert=True,
        )


def seed_user_recommendations(db) -> None:
    collection = db["UserRecommendations"]
    documents = [
        {
            "user_id": "user_123",
            "recommended_products": ["prod_101", "prod_205", "prod_333"],
            "last_updated": iso_dt("2024-01-10T08:00:00Z"),
        },
        {
            "user_id": "user_456",
            "recommended_products": ["prod_777", "prod_205", "prod_018"],
            "last_updated": iso_dt("2024-01-10T08:10:00Z"),
        },
    ]

    for doc in documents:
        collection.update_one(
            {"user_id": doc["user_id"]},
            {"$set": doc},
            upsert=True,
        )


def seed_moderation_queue(db) -> None:
    collection = db["ModerationQueue"]
    documents = [
        {
            "review_id": "rev_555",
            "user_id": "user_123",
            "product_id": "prod_101",
            "review_text": "Отличный товар, работает как нужно!",
            "rating": 5,
            "moderation_status": "pending",
            "flags": ["contains_images"],
            "submitted_at": iso_dt("2024-01-08T10:20:00Z"),
        },
        {
            "review_id": "rev_556",
            "user_id": "user_789",
            "product_id": "prod_205",
            "review_text": "Пришел с задержкой, но качество нормальное.",
            "rating": 4,
            "moderation_status": "in_review",
            "flags": ["delivery_complaint"],
            "submitted_at": iso_dt("2024-01-08T11:45:00Z"),
        },
    ]

    for doc in documents:
        collection.update_one(
            {"review_id": doc["review_id"]},
            {"$set": doc},
            upsert=True,
        )


def ensure_indexes(db) -> None:
    try:
        db["UserSessions"].create_index("session_id", unique=True)
        db["EventLogs"].create_index("event_id", unique=True)
        db["SupportTickets"].create_index("ticket_id", unique=True)
        db["UserRecommendations"].create_index("user_id", unique=True)
        db["ModerationQueue"].create_index("review_id", unique=True)
    except OperationFailure as exc:
        if exc.code == 13:
            print("Warning: createIndexes requires authentication. Skipping index creation.")
            return
        raise


def build_mongo_uri() -> str:
    explicit_uri = os.getenv("MONGO_URI")
    if explicit_uri:
        return explicit_uri

    user = os.getenv("MONGO_USER")
    password = os.getenv("MONGO_PASSWORD")
    auth_source = os.getenv("MONGO_AUTH_SOURCE", "admin")

    if user and password:
        return (
            f"mongodb://{user}:{password}@{DEFAULT_HOST}:{DEFAULT_PORT}/"
            f"?authSource={auth_source}"
        )

    return f"mongodb://{DEFAULT_HOST}:{DEFAULT_PORT}"


def main() -> None:
    mongo_uri = build_mongo_uri()
    client = MongoClient(mongo_uri)
    db = client[DB_NAME]

    ensure_indexes(db)
    seed_user_sessions(db)
    seed_event_logs(db)
    seed_support_tickets(db)
    seed_user_recommendations(db)
    seed_moderation_queue(db)

    print(f"MongoDB seeded successfully: {mongo_uri}, database='{DB_NAME}'")
    print("Collections:", ", ".join(sorted(db.list_collection_names())))


if __name__ == "__main__":
    main()
