import os


SECRET_KEY = os.environ.get("SUPERSET_SECRET_KEY", "fixed_secret_key_for_superset_3")
SQLALCHEMY_DATABASE_URI = os.environ.get(
    "SUPERSET_SQLALCHEMY_DATABASE_URI",
    "postgresql+psycopg2://superset:superset@postgres/superset",
)
SQLALCHEMY_TRACK_MODIFICATIONS = False
WTF_CSRF_ENABLED = True
ENABLE_PROXY_FIX = True
