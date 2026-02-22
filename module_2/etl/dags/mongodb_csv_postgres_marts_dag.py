import csv
import json
import os
from datetime import datetime, timedelta
from pathlib import Path

from airflow.decorators import dag, task
import psycopg2
from psycopg2 import sql


EXPORT_DIR = Path("/opt/airflow/dags/file/mongo_exports")

MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = int(os.getenv("MONGO_PORT", "27017"))
MONGO_DB = os.getenv("MONGO_DB", "dz_3_itog")
MONGO_USER = os.getenv("MONGO_USER", "root")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD", "example")
MONGO_AUTH_SOURCE = os.getenv("MONGO_AUTH_SOURCE", "admin")

POSTGRES_HOST = os.getenv("PG_HOST", "localhost")
POSTGRES_PORT = int(os.getenv("PG_PORT", "5432"))
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
POSTGRES_DB = os.getenv("POSTGRES_DB", "postgres")

PG_SCHEMA = "mongo_etl"


COLLECTION_CONFIG = {
    "UserSessions": {
        "file": "user_sessions.csv",
        "columns": [
            "session_id",
            "user_id",
            "start_time",
            "end_time",
            "pages_visited",
            "device",
            "actions",
        ],
        "pk": "session_id",
    },
    "EventLogs": {
        "file": "event_logs.csv",
        "columns": ["event_id", "timestamp", "event_type", "details"],
        "pk": "event_id",
    },
    "SupportTickets": {
        "file": "support_tickets.csv",
        "columns": [
            "ticket_id",
            "user_id",
            "status",
            "issue_type",
            "messages",
            "created_at",
            "updated_at",
        ],
        "pk": "ticket_id",
    },
    "UserRecommendations": {
        "file": "user_recommendations.csv",
        "columns": ["user_id", "recommended_products", "last_updated"],
        "pk": "user_id",
    },
    "ModerationQueue": {
        "file": "moderation_queue.csv",
        "columns": [
            "review_id",
            "user_id",
            "product_id",
            "review_text",
            "rating",
            "moderation_status",
            "flags",
            "submitted_at",
        ],
        "pk": "review_id",
    },
}


def _is_running_in_docker() -> bool:
    return os.path.exists("/.dockerenv")


def _resolve_host(host: str) -> str:
    if host == "localhost" and _is_running_in_docker():
        return "host.docker.internal"
    return host


def get_postgres_connection():
    return psycopg2.connect(
        host=_resolve_host(POSTGRES_HOST),
        port=POSTGRES_PORT,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        dbname=POSTGRES_DB,
    )


def build_mongo_uri() -> str:
    explicit_uri = os.getenv("MONGO_URI")
    if explicit_uri:
        return explicit_uri

    host = _resolve_host(MONGO_HOST)
    if MONGO_USER and MONGO_PASSWORD:
        return (
            f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{host}:{MONGO_PORT}/"
            f"?authSource={MONGO_AUTH_SOURCE}"
        )
    return f"mongodb://{host}:{MONGO_PORT}"


def _normalize_for_csv(value):
    if value is None:
        return ""
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, (list, dict)):
        return json.dumps(
            value,
            ensure_ascii=False,
            default=lambda obj: obj.isoformat() if isinstance(obj, datetime) else str(obj),
        )
    return str(value)


def _create_raw_tables(cur):
    cur.execute(sql.SQL("CREATE SCHEMA IF NOT EXISTS {}").format(sql.Identifier(PG_SCHEMA)))

    cur.execute(
        sql.SQL(
            """
            CREATE TABLE IF NOT EXISTS {}.raw_user_sessions_csv (
                session_id TEXT,
                user_id TEXT,
                start_time TEXT,
                end_time TEXT,
                pages_visited TEXT,
                device TEXT,
                actions TEXT
            )
            """
        ).format(sql.Identifier(PG_SCHEMA))
    )

    cur.execute(
        sql.SQL(
            """
            CREATE TABLE IF NOT EXISTS {}.raw_event_logs_csv (
                event_id TEXT,
                timestamp TEXT,
                event_type TEXT,
                details TEXT
            )
            """
        ).format(sql.Identifier(PG_SCHEMA))
    )

    cur.execute(
        sql.SQL(
            """
            CREATE TABLE IF NOT EXISTS {}.raw_support_tickets_csv (
                ticket_id TEXT,
                user_id TEXT,
                status TEXT,
                issue_type TEXT,
                messages TEXT,
                created_at TEXT,
                updated_at TEXT
            )
            """
        ).format(sql.Identifier(PG_SCHEMA))
    )

    cur.execute(
        sql.SQL(
            """
            CREATE TABLE IF NOT EXISTS {}.raw_user_recommendations_csv (
                user_id TEXT,
                recommended_products TEXT,
                last_updated TEXT
            )
            """
        ).format(sql.Identifier(PG_SCHEMA))
    )

    cur.execute(
        sql.SQL(
            """
            CREATE TABLE IF NOT EXISTS {}.raw_moderation_queue_csv (
                review_id TEXT,
                user_id TEXT,
                product_id TEXT,
                review_text TEXT,
                rating TEXT,
                moderation_status TEXT,
                flags TEXT,
                submitted_at TEXT
            )
            """
        ).format(sql.Identifier(PG_SCHEMA))
    )


def _create_staging_tables(cur):
    cur.execute(
        sql.SQL(
            """
            CREATE TABLE IF NOT EXISTS {}.stg_user_sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT,
                start_time TIMESTAMPTZ,
                end_time TIMESTAMPTZ,
                pages_visited JSONB,
                device JSONB,
                actions JSONB
            )
            """
        ).format(sql.Identifier(PG_SCHEMA))
    )
    cur.execute(
        sql.SQL(
            """
            CREATE TABLE IF NOT EXISTS {}.stg_event_logs (
                event_id TEXT PRIMARY KEY,
                event_ts TIMESTAMPTZ,
                event_type TEXT,
                details JSONB
            )
            """
        ).format(sql.Identifier(PG_SCHEMA))
    )
    cur.execute(
        sql.SQL(
            """
            CREATE TABLE IF NOT EXISTS {}.stg_support_tickets (
                ticket_id TEXT PRIMARY KEY,
                user_id TEXT,
                status TEXT,
                issue_type TEXT,
                messages JSONB,
                created_at TIMESTAMPTZ,
                updated_at TIMESTAMPTZ
            )
            """
        ).format(sql.Identifier(PG_SCHEMA))
    )
    cur.execute(
        sql.SQL(
            """
            CREATE TABLE IF NOT EXISTS {}.stg_user_recommendations (
                user_id TEXT PRIMARY KEY,
                recommended_products JSONB,
                last_updated TIMESTAMPTZ
            )
            """
        ).format(sql.Identifier(PG_SCHEMA))
    )
    cur.execute(
        sql.SQL(
            """
            CREATE TABLE IF NOT EXISTS {}.stg_moderation_queue (
                review_id TEXT PRIMARY KEY,
                user_id TEXT,
                product_id TEXT,
                review_text TEXT,
                rating INTEGER,
                moderation_status TEXT,
                flags JSONB,
                submitted_at TIMESTAMPTZ
            )
            """
        ).format(sql.Identifier(PG_SCHEMA))
    )


def _truncate_raw_tables(cur):
    table_names = [
        "raw_user_sessions_csv",
        "raw_event_logs_csv",
        "raw_support_tickets_csv",
        "raw_user_recommendations_csv",
        "raw_moderation_queue_csv",
    ]
    for table_name in table_names:
        cur.execute(
            sql.SQL("TRUNCATE TABLE {}.{}").format(
                sql.Identifier(PG_SCHEMA), sql.Identifier(table_name)
            )
        )


def _copy_csv_to_raw(cur, csv_path: Path, target_table: str):
    with csv_path.open("r", encoding="utf-8", newline="") as fh:
        cur.copy_expert(
            sql.SQL(
                "COPY {}.{} FROM STDIN WITH (FORMAT CSV, HEADER TRUE, QUOTE '\"', ESCAPE '\"')"
            ).format(sql.Identifier(PG_SCHEMA), sql.Identifier(target_table)).as_string(cur),
            fh,
        )


def _upsert_staging_tables(cur):
    cur.execute(
        sql.SQL(
            """
            INSERT INTO {}.stg_user_sessions (
                session_id, user_id, start_time, end_time, pages_visited, device, actions
            )
            SELECT
                session_id,
                user_id,
                NULLIF(start_time, '')::timestamptz,
                NULLIF(end_time, '')::timestamptz,
                COALESCE(NULLIF(pages_visited, ''), '[]')::jsonb,
                COALESCE(NULLIF(device, ''), '{{}}')::jsonb,
                COALESCE(NULLIF(actions, ''), '[]')::jsonb
            FROM {}.raw_user_sessions_csv
            ON CONFLICT (session_id) DO UPDATE SET
                user_id = EXCLUDED.user_id,
                start_time = EXCLUDED.start_time,
                end_time = EXCLUDED.end_time,
                pages_visited = EXCLUDED.pages_visited,
                device = EXCLUDED.device,
                actions = EXCLUDED.actions
            """
        ).format(sql.Identifier(PG_SCHEMA), sql.Identifier(PG_SCHEMA))
    )

    cur.execute(
        sql.SQL(
            """
            INSERT INTO {}.stg_event_logs (event_id, event_ts, event_type, details)
            SELECT
                event_id,
                NULLIF(timestamp, '')::timestamptz,
                event_type,
                COALESCE(NULLIF(details, ''), '{{}}')::jsonb
            FROM {}.raw_event_logs_csv
            ON CONFLICT (event_id) DO UPDATE SET
                event_ts = EXCLUDED.event_ts,
                event_type = EXCLUDED.event_type,
                details = EXCLUDED.details
            """
        ).format(sql.Identifier(PG_SCHEMA), sql.Identifier(PG_SCHEMA))
    )

    cur.execute(
        sql.SQL(
            """
            INSERT INTO {}.stg_support_tickets (
                ticket_id, user_id, status, issue_type, messages, created_at, updated_at
            )
            SELECT
                ticket_id,
                user_id,
                status,
                issue_type,
                COALESCE(NULLIF(messages, ''), '[]')::jsonb,
                NULLIF(created_at, '')::timestamptz,
                NULLIF(updated_at, '')::timestamptz
            FROM {}.raw_support_tickets_csv
            ON CONFLICT (ticket_id) DO UPDATE SET
                user_id = EXCLUDED.user_id,
                status = EXCLUDED.status,
                issue_type = EXCLUDED.issue_type,
                messages = EXCLUDED.messages,
                created_at = EXCLUDED.created_at,
                updated_at = EXCLUDED.updated_at
            """
        ).format(sql.Identifier(PG_SCHEMA), sql.Identifier(PG_SCHEMA))
    )

    cur.execute(
        sql.SQL(
            """
            INSERT INTO {}.stg_user_recommendations (user_id, recommended_products, last_updated)
            SELECT
                user_id,
                COALESCE(NULLIF(recommended_products, ''), '[]')::jsonb,
                NULLIF(last_updated, '')::timestamptz
            FROM {}.raw_user_recommendations_csv
            ON CONFLICT (user_id) DO UPDATE SET
                recommended_products = EXCLUDED.recommended_products,
                last_updated = EXCLUDED.last_updated
            """
        ).format(sql.Identifier(PG_SCHEMA), sql.Identifier(PG_SCHEMA))
    )

    cur.execute(
        sql.SQL(
            """
            INSERT INTO {}.stg_moderation_queue (
                review_id, user_id, product_id, review_text, rating, moderation_status, flags, submitted_at
            )
            SELECT
                review_id,
                user_id,
                product_id,
                review_text,
                NULLIF(rating, '')::integer,
                moderation_status,
                COALESCE(NULLIF(flags, ''), '[]')::jsonb,
                NULLIF(submitted_at, '')::timestamptz
            FROM {}.raw_moderation_queue_csv
            ON CONFLICT (review_id) DO UPDATE SET
                user_id = EXCLUDED.user_id,
                product_id = EXCLUDED.product_id,
                review_text = EXCLUDED.review_text,
                rating = EXCLUDED.rating,
                moderation_status = EXCLUDED.moderation_status,
                flags = EXCLUDED.flags,
                submitted_at = EXCLUDED.submitted_at
            """
        ).format(sql.Identifier(PG_SCHEMA), sql.Identifier(PG_SCHEMA))
    )


@dag(
    dag_id="mongodb_csv_postgres_marts",
    schedule=timedelta(days=1),
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["mongodb", "csv", "postgres", "etl", "marts"],
)
def mongodb_csv_postgres_marts_dag():
    @task
    def export_mongodb_to_csv():
        try:
            from pymongo import MongoClient
        except ImportError as exc:
            raise ImportError(
                "Для DAG требуется pymongo. Добавьте pymongo в _PIP_ADDITIONAL_REQUIREMENTS "
                "или в образ Airflow."
            ) from exc

        EXPORT_DIR.mkdir(parents=True, exist_ok=True)
        mongo_uri = build_mongo_uri()
        client = MongoClient(mongo_uri)
        db = client[MONGO_DB]

        exported = {}
        for collection_name, config in COLLECTION_CONFIG.items():
            csv_path = EXPORT_DIR / config["file"]
            cursor = db[collection_name].find({}, {"_id": 0})
            rows_written = 0
            with csv_path.open("w", encoding="utf-8", newline="") as fh:
                writer = csv.DictWriter(fh, fieldnames=config["columns"])
                writer.writeheader()
                for doc in cursor:
                    row = {col: _normalize_for_csv(doc.get(col)) for col in config["columns"]}
                    writer.writerow(row)
                    rows_written += 1

            exported[collection_name] = {"file": str(csv_path), "rows": rows_written}
            print(f"Exported {rows_written} rows from {collection_name} -> {csv_path}")

        return exported

    @task
    def load_csv_to_postgresql(exported_info: dict):
        conn = get_postgres_connection()
        conn.autocommit = False
        cur = conn.cursor()

        try:
            _create_raw_tables(cur)
            _create_staging_tables(cur)
            _truncate_raw_tables(cur)

            _copy_csv_to_raw(cur, Path(exported_info["UserSessions"]["file"]), "raw_user_sessions_csv")
            _copy_csv_to_raw(cur, Path(exported_info["EventLogs"]["file"]), "raw_event_logs_csv")
            _copy_csv_to_raw(cur, Path(exported_info["SupportTickets"]["file"]), "raw_support_tickets_csv")
            _copy_csv_to_raw(
                cur, Path(exported_info["UserRecommendations"]["file"]), "raw_user_recommendations_csv"
            )
            _copy_csv_to_raw(cur, Path(exported_info["ModerationQueue"]["file"]), "raw_moderation_queue_csv")

            _upsert_staging_tables(cur)
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cur.close()
            conn.close()

        print("CSV data loaded into PostgreSQL raw/staging tables successfully")
        return {"schema": PG_SCHEMA}

    @task
    def create_analytical_marts(_: dict):
        conn = get_postgres_connection()
        cur = conn.cursor()

        try:
            cur.execute(
                sql.SQL(
                    """
                    DROP TABLE IF EXISTS {}.mart_user_activity_daily;
                    CREATE TABLE {}.mart_user_activity_daily AS
                    WITH session_daily AS (
                        SELECT
                            user_id,
                            (start_time AT TIME ZONE 'UTC')::date AS activity_date,
                            COUNT(*) AS sessions_cnt,
                            ROUND(AVG(EXTRACT(EPOCH FROM (end_time - start_time)) / 60.0)::numeric, 2)
                                AS avg_session_minutes,
                            SUM(COALESCE(jsonb_array_length(pages_visited), 0)) AS pages_visited_total,
                            SUM(COALESCE(jsonb_array_length(actions), 0)) AS actions_total
                        FROM {}.stg_user_sessions
                        GROUP BY user_id, (start_time AT TIME ZONE 'UTC')::date
                    ),
                    ticket_daily AS (
                        SELECT
                            user_id,
                            (created_at AT TIME ZONE 'UTC')::date AS activity_date,
                            COUNT(*) AS tickets_created_cnt,
                            COUNT(*) FILTER (WHERE status = 'open') AS tickets_open_cnt
                        FROM {}.stg_support_tickets
                        GROUP BY user_id, (created_at AT TIME ZONE 'UTC')::date
                    ),
                    recommendation_users AS (
                        SELECT
                            user_id,
                            jsonb_array_length(recommended_products) AS recommended_products_cnt
                        FROM {}.stg_user_recommendations
                    )
                    SELECT
                        COALESCE(s.user_id, t.user_id) AS user_id,
                        COALESCE(s.activity_date, t.activity_date) AS activity_date,
                        COALESCE(s.sessions_cnt, 0) AS sessions_cnt,
                        COALESCE(s.avg_session_minutes, 0) AS avg_session_minutes,
                        COALESCE(s.pages_visited_total, 0) AS pages_visited_total,
                        COALESCE(s.actions_total, 0) AS actions_total,
                        COALESCE(t.tickets_created_cnt, 0) AS tickets_created_cnt,
                        COALESCE(t.tickets_open_cnt, 0) AS tickets_open_cnt,
                        COALESCE(r.recommended_products_cnt, 0) AS recommended_products_cnt
                    FROM session_daily s
                    FULL OUTER JOIN ticket_daily t
                        ON s.user_id = t.user_id
                       AND s.activity_date = t.activity_date
                    LEFT JOIN recommendation_users r
                        ON r.user_id = COALESCE(s.user_id, t.user_id);
                    """
                ).format(
                    sql.Identifier(PG_SCHEMA),
                    sql.Identifier(PG_SCHEMA),
                    sql.Identifier(PG_SCHEMA),
                    sql.Identifier(PG_SCHEMA),
                    sql.Identifier(PG_SCHEMA),
                )
            )

            cur.execute(
                sql.SQL(
                    """
                    DROP TABLE IF EXISTS {}.mart_product_quality;
                    CREATE TABLE {}.mart_product_quality AS
                    WITH moderation AS (
                        SELECT
                            product_id,
                            COUNT(*) AS reviews_total,
                            ROUND(AVG(rating)::numeric, 2) AS avg_rating,
                            COUNT(*) FILTER (WHERE moderation_status = 'pending') AS pending_reviews_cnt,
                            COUNT(*) FILTER (WHERE flags @> '["contains_images"]'::jsonb)
                                AS reviews_with_images_cnt,
                            MIN((submitted_at AT TIME ZONE 'UTC')::date) AS first_review_date,
                            MAX((submitted_at AT TIME ZONE 'UTC')::date) AS last_review_date
                        FROM {}.stg_moderation_queue
                        GROUP BY product_id
                    ),
                    recommendations AS (
                        SELECT
                            rec.product_id,
                            COUNT(DISTINCT ur.user_id) AS recommended_users_cnt
                        FROM {}.stg_user_recommendations ur
                        CROSS JOIN LATERAL jsonb_array_elements_text(ur.recommended_products) AS rec(product_id)
                        GROUP BY rec.product_id
                    )
                    SELECT
                        COALESCE(m.product_id, r.product_id) AS product_id,
                        COALESCE(m.reviews_total, 0) AS reviews_total,
                        COALESCE(m.avg_rating, 0) AS avg_rating,
                        COALESCE(m.pending_reviews_cnt, 0) AS pending_reviews_cnt,
                        COALESCE(m.reviews_with_images_cnt, 0) AS reviews_with_images_cnt,
                        COALESCE(r.recommended_users_cnt, 0) AS recommended_users_cnt,
                        m.first_review_date,
                        m.last_review_date
                    FROM moderation m
                    FULL OUTER JOIN recommendations r
                        ON m.product_id = r.product_id;
                    """
                ).format(
                    sql.Identifier(PG_SCHEMA),
                    sql.Identifier(PG_SCHEMA),
                    sql.Identifier(PG_SCHEMA),
                    sql.Identifier(PG_SCHEMA),
                )
            )

            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cur.close()
            conn.close()

        print(f"Created 2 marts in schema '{PG_SCHEMA}': mart_user_activity_daily, mart_product_quality")

    create_analytical_marts(load_csv_to_postgresql(export_mongodb_to_csv()))


mongodb_csv_postgres_marts = mongodb_csv_postgres_marts_dag()
