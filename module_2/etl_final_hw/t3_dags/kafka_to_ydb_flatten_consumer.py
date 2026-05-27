import argparse
import os
import posixpath
import subprocess
import sys
from typing import Any, Dict, Iterable, List

from pyspark.sql import SparkSession
from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import (
    ArrayType,
    IntegerType,
    StringType,
    StructField,
    StructType,
)


def ensure_ydb_sdk() -> None:
    try:
        import ydb  # noqa: F401
    except ImportError:
        subprocess.check_call([
            sys.executable,
            "-m",
            "pip",
            "install",
            "--user",
            "ydb",
        ])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument("--kafka-bootstrap-servers", required=True)
    parser.add_argument("--kafka-topic", required=True)
    parser.add_argument("--kafka-username", required=True)
    parser.add_argument("--kafka-password", required=True)

    parser.add_argument("--ydb-endpoint", required=True)
    parser.add_argument("--ydb-database", required=True)
    parser.add_argument("--ydb-table", required=True)

    parser.add_argument("--checkpoint-path", required=True)

    return parser.parse_args()


def get_schema() -> StructType:
    return StructType([
        StructField("application_id", StringType(), True),
        StructField("customer", StructType([
            StructField("customer_id", StringType(), True),
        ]), True),
        StructField("region", StringType(), True),
        StructField("loan", StructType([
            StructField("amount", IntegerType(), True),
        ]), True),
        StructField("term_months", IntegerType(), True),
        StructField("scoring", StructType([
            StructField("score", IntegerType(), True),
        ]), True),
        StructField("risk_level", StringType(), True),
        StructField("documents", ArrayType(StructType([
            StructField("type", StringType(), True),
            StructField("status", StringType(), True),
        ])), True),
        StructField("decision_status", StringType(), True),
        StructField("submitted_at", StringType(), True),
    ])


def build_ydb_column_types() -> Any:
    import ydb

    return (
        ydb.BulkUpsertColumns()
        .add_column("application_id", ydb.PrimitiveType.Utf8)
        .add_column("customer_id", ydb.OptionalType(ydb.PrimitiveType.Utf8))
        .add_column("region", ydb.OptionalType(ydb.PrimitiveType.Utf8))
        .add_column("loan_amount", ydb.OptionalType(ydb.PrimitiveType.Int64))
        .add_column("term_months", ydb.OptionalType(ydb.PrimitiveType.Int32))
        .add_column("scoring_score", ydb.OptionalType(ydb.PrimitiveType.Int32))
        .add_column("risk_level", ydb.OptionalType(ydb.PrimitiveType.Utf8))
        .add_column("first_document_type", ydb.OptionalType(ydb.PrimitiveType.Utf8))
        .add_column("first_document_status", ydb.OptionalType(ydb.PrimitiveType.Utf8))
        .add_column("documents_count", ydb.OptionalType(ydb.PrimitiveType.Int32))
        .add_column("decision_status", ydb.OptionalType(ydb.PrimitiveType.Utf8))
        .add_column("submitted_at", ydb.OptionalType(ydb.PrimitiveType.Utf8))
        .add_column("kafka_topic", ydb.OptionalType(ydb.PrimitiveType.Utf8))
        .add_column("kafka_partition", ydb.OptionalType(ydb.PrimitiveType.Int32))
        .add_column("kafka_offset", ydb.OptionalType(ydb.PrimitiveType.Int64))
        .add_column("processed_at", ydb.OptionalType(ydb.PrimitiveType.Utf8))
    )


def row_to_dict(row: Any) -> Dict[str, Any]:
    return {
        "application_id": row["application_id"],
        "customer_id": row["customer_id"],
        "region": row["region"],
        "loan_amount": row["loan_amount"],
        "term_months": row["term_months"],
        "scoring_score": row["scoring_score"],
        "risk_level": row["risk_level"],
        "first_document_type": row["first_document_type"],
        "first_document_status": row["first_document_status"],
        "documents_count": row["documents_count"],
        "decision_status": row["decision_status"],
        "submitted_at": row["submitted_at"],
        "kafka_topic": row["kafka_topic"],
        "kafka_partition": row["kafka_partition"],
        "kafka_offset": row["kafka_offset"],
        "processed_at": row["processed_at"],
    }


def write_rows_to_ydb(
    rows: Iterable[Any],
    ydb_endpoint: str,
    ydb_database: str,
    ydb_table: str,
    batch_size: int = 1000,
) -> None:
    ensure_ydb_sdk()
    import ydb

    os.environ["USE_METADATA_CREDENTIALS"] = "1"

    driver = ydb.Driver(
        endpoint=ydb_endpoint,
        database=ydb_database,
        credentials=ydb.credentials_from_env_variables(),
    )
    driver.wait(fail_fast=True, timeout=30)

    table_path = posixpath.join(ydb_database, ydb_table)
    column_types = build_ydb_column_types()

    batch: List[Dict[str, Any]] = []

    try:
        for row in rows:
            item = row_to_dict(row)

            if item["application_id"] is None:
                continue

            batch.append(item)

            if len(batch) >= batch_size:
                driver.table_client.bulk_upsert(table_path, batch, column_types)
                batch.clear()

        if batch:
            driver.table_client.bulk_upsert(table_path, batch, column_types)
    finally:
        driver.stop()


def main() -> None:
    ensure_ydb_sdk()
    args = parse_args()

    spark = (
        SparkSession.builder
        .appName("hw3_kafka_to_ydb_flatten")
        .getOrCreate()
    )

    jaas_config = (
        "org.apache.kafka.common.security.scram.ScramLoginModule required "
        f'username="{args.kafka_username}" '
        f'password="{args.kafka_password}";'
    )

    kafka_df = (
        spark.readStream
        .format("kafka")
        .option("kafka.bootstrap.servers", args.kafka_bootstrap_servers)
        .option("subscribe", args.kafka_topic)
        .option("startingOffsets", "earliest")
        .option("failOnDataLoss", "false")
        .option("kafka.security.protocol", "SASL_SSL")
        .option("kafka.sasl.mechanism", "SCRAM-SHA-512")
        .option("kafka.sasl.jaas.config", jaas_config)
        .load()
    )

    schema = get_schema()

    parsed_df = (
        kafka_df
        .select(
            F.col("topic").alias("kafka_topic"),
            F.col("partition").cast("int").alias("kafka_partition"),
            F.col("offset").cast("long").alias("kafka_offset"),
            F.col("value").cast("string").alias("json_value"),
        )
        .withColumn("data", F.from_json(F.col("json_value"), schema))
    )

    flat_df = (
        parsed_df
        .select(
            F.col("data.application_id").alias("application_id"),
            F.col("data.customer.customer_id").alias("customer_id"),
            F.col("data.region").alias("region"),
            F.col("data.loan.amount").cast("long").alias("loan_amount"),
            F.col("data.term_months").cast("int").alias("term_months"),
            F.col("data.scoring.score").cast("int").alias("scoring_score"),
            F.col("data.risk_level").alias("risk_level"),
            F.col("data.documents").getItem(0).getField("type").alias("first_document_type"),
            F.col("data.documents").getItem(0).getField("status").alias("first_document_status"),
            F.size(F.col("data.documents")).cast("int").alias("documents_count"),
            F.col("data.decision_status").alias("decision_status"),
            F.col("data.submitted_at").alias("submitted_at"),
            F.col("kafka_topic"),
            F.col("kafka_partition"),
            F.col("kafka_offset"),
            F.date_format(F.current_timestamp(), "yyyy-MM-dd'T'HH:mm:ss'Z'").alias("processed_at"),
        )
        .filter(F.col("application_id").isNotNull())
    )

    def foreach_batch(batch_df: DataFrame, batch_id: int) -> None:
        count = batch_df.count()
        print(f"Processing batch_id={batch_id}, rows={count}")

        if count == 0:
            return

        write_rows_to_ydb(
            rows=batch_df.toLocalIterator(),
            ydb_endpoint=args.ydb_endpoint,
            ydb_database=args.ydb_database,
            ydb_table=args.ydb_table,
            batch_size=1000,
        )

    query = (
        flat_df.writeStream
        .foreachBatch(foreach_batch)
        .option("checkpointLocation", args.checkpoint_path)
        .trigger(once=True)
        .start()
    )

    query.awaitTermination()
    spark.stop()


if __name__ == "__main__":
    main()