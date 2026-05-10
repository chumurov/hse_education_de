from __future__ import annotations

import os
import tempfile
from pathlib import Path

import boto3
import numpy as np
import pandas as pd
import pendulum
from airflow.decorators import dag, task
from airflow.exceptions import AirflowFailException
from sklearn.ensemble import IsolationForest, RandomForestClassifier, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import accuracy_score, mean_absolute_error, mean_squared_error, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sqlalchemy import create_engine, text


SOURCE_SQL_DIR = Path(os.environ.get("ML_SOURCE_SQL_DIR", "/opt/airflow/ml_seed_sql"))

POSTGRES_HOST = os.environ.get("ML_POSTGRES_HOST", "postgres")
POSTGRES_PORT = int(os.environ.get("ML_POSTGRES_PORT", "5432"))
POSTGRES_DB = os.environ.get("ML_POSTGRES_DB", "postgres")
POSTGRES_USER = os.environ.get("ML_POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.environ.get("ML_POSTGRES_PASSWORD", "postgres")

MINIO_ENDPOINT = os.environ.get("ML_MINIO_ENDPOINT", "http://minio:9000")
MINIO_BUCKET = os.environ.get("ML_MINIO_BUCKET", "mentor-hw")
MINIO_ACCESS_KEY = os.environ.get("MINIO_ROOT_USER", "minioadmin")
MINIO_SECRET_KEY = os.environ.get("MINIO_ROOT_PASSWORD", "minioadmin123")

RAW_PREFIX = "ml/raw"
CURATED_PREFIX = "ml/curated"

DATA_SCHEMAS = ["public", "analytics", "ml"]

SQL_SCRIPT_GROUPS = [
    ("task1ddl (1).sql", "1task (1).sql"),
    ("task2ddl (1).sql", "2task (1).sql"),
    ("task3ddl (1).sql", "task3 (1).sql"),
    ("tak4ddl (1).sql", "task4 (1).sql"),
    ("oil_station (1).sql", None),
]

SOURCE_TABLES = [
    "wells",
    "production",
    "well_telemetry",
    "well_targets",
    "pumps",
    "pump_sensors",
    "pump_failures",
    "deliveries",
    "drivers",
    "vehicles",
    "oil_stations",
]


def make_postgres_engine(database: str | None = None):
    target_database = database or POSTGRES_DB
    url = (
        f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
        f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{target_database}"
    )
    return create_engine(url, pool_pre_ping=True)


def make_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=MINIO_ENDPOINT,
        aws_access_key_id=MINIO_ACCESS_KEY,
        aws_secret_access_key=MINIO_SECRET_KEY,
    )


def ensure_bucket(client) -> None:
    try:
        client.head_bucket(Bucket=MINIO_BUCKET)
    except Exception:
        client.create_bucket(Bucket=MINIO_BUCKET)


def upload_dataframe(client, df: pd.DataFrame, key: str) -> None:
    with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as handle:
        temp_path = Path(handle.name)
    try:
        df.to_parquet(temp_path, index=False)
        client.upload_file(str(temp_path), MINIO_BUCKET, key)
    finally:
        if temp_path.exists():
            temp_path.unlink()


def download_dataframe(client, key: str) -> pd.DataFrame:
    with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as handle:
        temp_path = Path(handle.name)
    try:
        client.download_file(MINIO_BUCKET, key, str(temp_path))
        return pd.read_parquet(temp_path)
    finally:
        if temp_path.exists():
            temp_path.unlink()


def load_sql_file(engine, path: Path) -> None:
    if not path.exists():
        raise AirflowFailException(f"Missing SQL file: {path}")

    sql_text = path.read_text(encoding="utf-8").strip()
    if not sql_text:
        return

    with engine.begin() as connection:
        connection.exec_driver_sql(sql_text)


def drop_and_seed_sources() -> None:
    engine = make_postgres_engine()
    drop_tables(engine, DATA_SCHEMAS)

    for ddl_name, dml_name in SQL_SCRIPT_GROUPS:
        load_sql_file(engine, SOURCE_SQL_DIR / ddl_name)
        if dml_name is not None:
            load_sql_file(engine, SOURCE_SQL_DIR / dml_name)


def read_table(engine, table_name: str, schema: str = "public") -> pd.DataFrame:
    query = text(f'SELECT * FROM "{schema}"."{table_name}"')
    return pd.read_sql_query(query, engine)


def normalize_temporal_columns(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    for column in result.columns:
        if column.lower().endswith(("date", "_date", "timestamp", "_time", "time")):
            result[column] = pd.to_datetime(result[column], errors="coerce")
    return result


def fill_nulls(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    for column in result.columns:
        if pd.api.types.is_numeric_dtype(result[column]):
            result[column] = pd.to_numeric(result[column], errors="coerce")
            if result[column].isna().all():
                result[column] = result[column].fillna(0)
            else:
                result[column] = result[column].fillna(result[column].median())
        elif pd.api.types.is_datetime64_any_dtype(result[column]):
            result[column] = result[column].fillna(method="ffill").fillna(method="bfill")
        else:
            mode = result[column].mode(dropna=True)
            fill_value = mode.iloc[0] if not mode.empty else "unknown"
            result[column] = result[column].fillna(fill_value)
    return result


def remove_outliers(df: pd.DataFrame, numeric_columns: list[str], threshold: float = 3.0) -> pd.DataFrame:
    if df.empty or not numeric_columns:
        return df.copy()

    mask = pd.Series(True, index=df.index)
    for column in numeric_columns:
        if column not in df.columns:
            continue
        series = pd.to_numeric(df[column], errors="coerce")
        std = series.std(ddof=0)
        if pd.isna(std) or std == 0:
            continue
        z_score = ((series - series.mean()) / std).abs()
        mask &= z_score.fillna(0) <= threshold
    return df.loc[mask].reset_index(drop=True)


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    prepared = normalize_temporal_columns(df)
    prepared = fill_nulls(prepared)
    numeric_columns = prepared.select_dtypes(include=[np.number]).columns.tolist()
    prepared = remove_outliers(prepared, numeric_columns)
    return prepared.drop_duplicates().reset_index(drop=True)


def ensure_schema(engine, schema_name: str) -> None:
    with engine.begin() as connection:
        connection.exec_driver_sql(f'CREATE SCHEMA IF NOT EXISTS "{schema_name}"')


def drop_tables(engine, schema_names: list[str]) -> None:
    schema_list = ", ".join(f"'{schema_name}'" for schema_name in schema_names)
    query = text(
        f"""
        SELECT table_schema, table_name
        FROM information_schema.tables
        WHERE table_schema IN ({schema_list})
          AND table_type = 'BASE TABLE'
        ORDER BY table_schema, table_name
        """
    )
    with engine.begin() as connection:
        for schema_name, table_name in connection.execute(query):
            connection.exec_driver_sql(f'DROP TABLE IF EXISTS "{schema_name}"."{table_name}" CASCADE')


@dag(
    dag_id="ml_postgres_s3_pipeline",
    start_date=pendulum.datetime(2026, 5, 10, tz="UTC"),
    schedule=None,
    catchup=False,
    tags=["postgres", "minio", "pandas", "sklearn", "ml"],
    default_args={"owner": "airflow", "retries": 1},
)
def ml_postgres_s3_pipeline():
    @task
    def ingest_source_sql() -> str:
        drop_and_seed_sources()
        return "sources_loaded"

    @task
    def export_raw_tables(_: str) -> list[str]:
        engine = make_postgres_engine()
        client = make_s3_client()
        ensure_bucket(client)

        exported_keys: list[str] = []
        for table_name in SOURCE_TABLES:
            frame = read_table(engine, table_name)
            raw_key = f"{RAW_PREFIX}/{table_name}.parquet"
            upload_dataframe(client, frame, raw_key)
            exported_keys.append(raw_key)
        return exported_keys

    @task
    def drop_source_tables(_: list[str]) -> str:
        engine = make_postgres_engine()
        drop_tables(engine, ["public"])
        return "public_dropped"

    @task
    def clean_and_curate(raw_keys: list[str]) -> list[str]:
        client = make_s3_client()
        curated_keys: list[str] = []

        for raw_key in raw_keys:
            table_name = Path(raw_key).stem
            frame = download_dataframe(client, raw_key)
            curated_frame = clean_dataframe(frame)
            curated_key = f"{CURATED_PREFIX}/{table_name}.parquet"
            upload_dataframe(client, curated_frame, curated_key)
            curated_keys.append(curated_key)

        return curated_keys

    @task
    def build_postgres_marts(curated_keys: list[str]) -> dict[str, str]:
        client = make_s3_client()
        engine = make_postgres_engine()
        ensure_schema(engine, "analytics")

        curated = {
            Path(key).stem: download_dataframe(client, key)
            for key in curated_keys
        }

        wells = curated["wells"]
        production = normalize_temporal_columns(curated["production"])
        production["date"] = pd.to_datetime(production["date"]).dt.date
        production_dashboard = (
            production.merge(wells, on="well_id", how="left")
            .loc[
                :,
                [
                    "date",
                    "well_id",
                    "name",
                    "field_name",
                    "region",
                    "status",
                    "oil_ton",
                    "gas_m3",
                    "water_m3",
                    "energy_kwh",
                    "downtime_hours",
                    "temperature",
                    "pressure",
                ],
            ]
            .sort_values(["date", "well_id"])
            .reset_index(drop=True)
        )

        deliveries = normalize_temporal_columns(curated["deliveries"])
        deliveries["cost_per_km"] = deliveries["cost_usd"] / deliveries["distance_km"].replace(0, np.nan)
        deliveries["distance_bucket"] = pd.cut(
            deliveries["distance_km"],
            bins=[0, 100, 150, 200, 1000],
            labels=["short", "medium", "long", "very_long"],
            include_lowest=True,
        )
        logistics_dashboard = (
            deliveries.merge(
                curated["drivers"].rename(columns={"name": "driver_name", "region": "driver_region"}),
                on="driver_id",
                how="left",
            )
            .merge(curated["vehicles"].rename(columns={"fuel_type": "vehicle_fuel_type"}), on="vehicle_id", how="left")
        )
        logistics_dashboard["late_flag"] = (logistics_dashboard["delay_hours"] > 0).astype(int)
        logistics_dashboard = logistics_dashboard[
            [
                "delivery_id",
                "date",
                "source",
                "destination",
                "product_type",
                "volume_ton",
                "cost_usd",
                "delay_hours",
                "distance_km",
                "distance_bucket",
                "weather_conditions",
                "driver_id",
                "driver_name",
                "experience_years",
                "driver_region",
                "vehicle_id",
                "plate_number",
                "capacity_ton",
                "vehicle_fuel_type",
                "cost_per_km",
                "late_flag",
            ]
        ].sort_values(["date", "delivery_id"]).reset_index(drop=True)

        marts = {
            "analytics.production_dashboard": production_dashboard,
            "analytics.logistics_dashboard": logistics_dashboard,
        }

        for qualified_name, frame in marts.items():
            schema_name, table_name = qualified_name.split(".", 1)
            ensure_schema(engine, schema_name)
            frame.to_sql(table_name, engine, schema=schema_name, if_exists="replace", index=False, method="multi")

        return {name: str(len(frame)) for name, frame in marts.items()}

    @task
    def train_debit_model(curated_keys: list[str]) -> dict[str, str]:
        client = make_s3_client()
        engine = make_postgres_engine()
        ensure_schema(engine, "ml")

        curated = {Path(key).stem: download_dataframe(client, key) for key in curated_keys}
        wells = curated["wells"]
        production = normalize_temporal_columns(curated["production"])
        production["date"] = pd.to_datetime(production["date"]).dt.normalize()
        production = production.merge(wells[["well_id", "name", "field_name", "region", "status"]], on="well_id", how="left")

        dataset = production[
            [
                "well_id",
                "date",
                "name",
                "field_name",
                "region",
                "status",
                "oil_ton",
                "gas_m3",
                "water_m3",
                "energy_kwh",
                "downtime_hours",
                "temperature",
                "pressure",
            ]
        ].copy()

        if dataset.empty:
            raise AirflowFailException("Debit dataset is empty after merge with targets")

        feature_columns = ["gas_m3", "water_m3", "energy_kwh", "downtime_hours", "temperature", "pressure"]
        dataset = dataset.sort_values(["date", "well_id"]).reset_index(drop=True)
        unique_dates = sorted(dataset["date"].unique())
        cutoff = max(1, int(len(unique_dates) * 0.8))
        train_dates = set(unique_dates[:cutoff])
        train_frame = dataset[dataset["date"].isin(train_dates)].copy()
        test_frame = dataset[~dataset["date"].isin(train_dates)].copy()

        if test_frame.empty:
            train_frame, test_frame = train_test_split(dataset, test_size=0.25, random_state=42)

        X_train = train_frame[feature_columns]
        y_train = train_frame["oil_ton"]
        X_test = test_frame[feature_columns]
        y_test = test_frame["oil_ton"]

        models = {
            "linear_regression": make_pipeline(SimpleImputer(strategy="median"), LinearRegression()),
            "random_forest": make_pipeline(
                SimpleImputer(strategy="median"),
                RandomForestRegressor(n_estimators=200, random_state=42),
            ),
        }

        metrics_rows = []
        fitted_models = {}
        for name, model in models.items():
            model.fit(X_train, y_train)
            fitted_models[name] = model
            predictions = model.predict(X_test)
            metrics_rows.append(
                {
                    "model_name": name,
                    "mae": float(mean_absolute_error(y_test, predictions)),
                    "rmse": float(np.sqrt(mean_squared_error(y_test, predictions))),
                }
            )

        metrics = pd.DataFrame(metrics_rows).sort_values(["rmse", "mae"])
        best_model_name = metrics.iloc[0]["model_name"]
        full_model = make_pipeline(SimpleImputer(strategy="median"), LinearRegression()) if best_model_name == "linear_regression" else make_pipeline(
            SimpleImputer(strategy="median"),
            RandomForestRegressor(n_estimators=200, random_state=42),
        )
        full_model.fit(dataset[feature_columns], dataset["oil_ton"])

        debit_dashboard = dataset[
            [
                "well_id",
                "date",
                "name",
                "field_name",
                "region",
                "status",
                "oil_ton",
            ]
            + feature_columns
        ].copy()
        debit_dashboard = debit_dashboard.rename(columns={"oil_ton": "daily_oil_ton"})
        debit_dashboard["predicted_daily_oil_ton"] = full_model.predict(dataset[feature_columns])
        debit_dashboard["error"] = debit_dashboard["daily_oil_ton"] - debit_dashboard["predicted_daily_oil_ton"]
        debit_dashboard["abs_error"] = debit_dashboard["error"].abs()
        debit_dashboard["pct_error"] = debit_dashboard["abs_error"] / debit_dashboard["daily_oil_ton"].replace(0, np.nan)
        debit_dashboard["model_name"] = best_model_name
        debit_dashboard["prediction_type"] = "daily"
        debit_dashboard = debit_dashboard.sort_values(["date", "well_id"]).reset_index(drop=True)

        debit_dashboard.to_sql("debit_dashboard", engine, schema="ml", if_exists="replace", index=False, method="multi")

        return {"best_model": best_model_name, "dashboard_rows": str(len(debit_dashboard))}

    @task
    def train_failure_model(curated_keys: list[str]) -> dict[str, str]:
        client = make_s3_client()
        engine = make_postgres_engine()
        ensure_schema(engine, "ml")

        curated = {Path(key).stem: download_dataframe(client, key) for key in curated_keys}
        pumps = curated["pumps"].merge(curated["wells"], on="well_id", how="left")
        sensors = normalize_temporal_columns(curated["pump_sensors"])
        failures = normalize_temporal_columns(curated["pump_failures"])

        sensors["timestamp"] = pd.to_datetime(sensors["timestamp"])
        failures["failure_date"] = pd.to_datetime(failures["failure_date"])
        feature_columns = ["temperature", "vibration", "current", "rpm", "pressure"]
        sensor_features = sensors.copy()
        sensor_features[feature_columns] = sensor_features[feature_columns].apply(pd.to_numeric, errors="coerce")
        sensor_features = fill_nulls(sensor_features)

        iso = IsolationForest(contamination=0.1, random_state=42)
        iso.fit(sensor_features[feature_columns])
        sensor_features["anomaly_score"] = -iso.score_samples(sensor_features[feature_columns])
        sensor_features["is_anomaly"] = (iso.predict(sensor_features[feature_columns]) == -1).astype(int)

        sensor_features = sensor_features.reset_index(drop=True)
        sensor_features["row_id"] = sensor_features.index
        sensor_features = sensor_features.merge(
            pumps[["pump_id", "well_id", "name", "field_name", "region", "status"]],
            on="pump_id",
            how="left",
        )

        if failures.empty:
            sensor_features["failure_within_24h"] = 0
        else:
            merged = sensor_features[["row_id", "pump_id", "timestamp"]].merge(
                failures[["pump_id", "failure_date"]],
                on="pump_id",
                how="left",
            )
            merged["within_window"] = merged["failure_date"].between(
                merged["timestamp"],
                merged["timestamp"] + pd.Timedelta(hours=24),
            )
            labels = merged.groupby("row_id")["within_window"].any().astype(int)
            sensor_features["failure_within_24h"] = sensor_features["row_id"].map(labels).fillna(0).astype(int)

        anomaly_min = float(sensor_features["anomaly_score"].min())
        anomaly_max = float(sensor_features["anomaly_score"].max())
        if anomaly_max > anomaly_min:
            anomaly_norm = (sensor_features["anomaly_score"] - anomaly_min) / (anomaly_max - anomaly_min)
        else:
            anomaly_norm = pd.Series(0.0, index=sensor_features.index)
        sensor_features["risk_score"] = 0.6 * anomaly_norm + 0.4 * sensor_features["failure_within_24h"]

        if sensor_features["failure_within_24h"].nunique() < 2:
            raise AirflowFailException("Failure label contains only one class; cannot train classifier")

        X_train, X_test, y_train, y_test = train_test_split(
            sensor_features[feature_columns],
            sensor_features["failure_within_24h"],
            test_size=0.25,
            random_state=42,
            stratify=sensor_features["failure_within_24h"],
        )

        classifier = make_pipeline(
            SimpleImputer(strategy="median"),
            RandomForestClassifier(n_estimators=250, random_state=42, class_weight="balanced"),
        )
        classifier.fit(X_train, y_train)
        probabilities = classifier.predict_proba(X_test)[:, 1]
        predictions = (probabilities >= 0.5).astype(int)

        roc_auc = float("nan")
        if y_test.nunique() > 1:
            roc_auc = float(roc_auc_score(y_test, probabilities))

        pump_risk_dashboard = sensor_features[["pump_id", "well_id", "name", "field_name", "region", "status", "timestamp", "risk_score", "anomaly_score", "is_anomaly", "failure_within_24h"] + feature_columns].copy()
        pump_risk_dashboard["failure_probability"] = classifier.predict_proba(sensor_features[feature_columns])[:, 1]
        pump_risk_dashboard.to_sql("pump_risk_dashboard", engine, schema="ml", if_exists="replace", index=False, method="multi")

        return {"risk_rows": str(len(pump_risk_dashboard)), "roc_auc": f"{roc_auc:.3f}" if not np.isnan(roc_auc) else "nan"}

    @task
    def analyze_deliveries(curated_keys: list[str]) -> dict[str, str]:
        client = make_s3_client()
        engine = make_postgres_engine()
        ensure_schema(engine, "analytics")

        curated = {Path(key).stem: download_dataframe(client, key) for key in curated_keys}
        deliveries = normalize_temporal_columns(curated["deliveries"])
        drivers = curated["drivers"]
        vehicles = curated["vehicles"]

        deliveries["cost_per_km"] = deliveries["cost_usd"] / deliveries["distance_km"].replace(0, np.nan)
        deliveries["distance_bucket"] = pd.cut(
            deliveries["distance_km"],
            bins=[0, 100, 150, 200, 1000],
            labels=["short", "medium", "long", "very_long"],
            include_lowest=True,
        )

        driver_named = deliveries.merge(
            drivers.rename(columns={"name": "driver_name", "region": "driver_region"}),
            on="driver_id",
            how="left",
        )
        vehicle_named = driver_named.merge(
            vehicles.rename(columns={"fuel_type": "vehicle_fuel_type"}),
            on="vehicle_id",
            how="left",
        )
        vehicle_named["late_flag"] = (vehicle_named["delay_hours"] > 0).astype(int)

        logistics_dashboard = vehicle_named[
            [
                "delivery_id",
                "date",
                "source",
                "destination",
                "product_type",
                "volume_ton",
                "cost_usd",
                "delay_hours",
                "late_flag",
                "distance_km",
                "cost_per_km",
                "distance_bucket",
                "weather_conditions",
                "driver_id",
                "driver_name",
                "experience_years",
                "driver_region",
                "vehicle_id",
                "plate_number",
                "capacity_ton",
                "vehicle_fuel_type",
            ]
        ].copy()

        outputs = {
            "analytics.logistics_dashboard": logistics_dashboard,
        }

        for qualified_name, frame in outputs.items():
            schema_name, table_name = qualified_name.split(".", 1)
            ensure_schema(engine, schema_name)
            frame.to_sql(table_name, engine, schema=schema_name, if_exists="replace", index=False, method="multi")

        return {name: str(len(frame)) for name, frame in outputs.items()}

    loaded = ingest_source_sql()
    exported = export_raw_tables(loaded)
    dropped = drop_source_tables(exported)
    curated = clean_and_curate(exported)
    marts = build_postgres_marts(curated)
    debit = train_debit_model(curated)
    failure = train_failure_model(curated)
    deliveries = analyze_deliveries(curated)

    loaded >> exported >> dropped >> curated >> marts >> debit >> failure >> deliveries


ml_postgres_s3_pipeline()
