import argparse

from pyspark.sql import SparkSession
from pyspark.sql import functions as F


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-path", required=True)
    parser.add_argument("--kafka-bootstrap-servers", required=True)
    parser.add_argument("--kafka-topic", required=True)
    parser.add_argument("--kafka-username", required=True)
    parser.add_argument("--kafka-password", required=True)
    parser.add_argument("--json-format", choices=["array", "jsonl"], default="array")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    spark = (
        SparkSession.builder
        .appName("hw3_s3_json_to_kafka")
        .getOrCreate()
    )

    multiline = "true" if args.json_format == "array" else "false"

    df = (
        spark.read
        .option("multiLine", multiline)
        .json(args.input_path)
    )

    kafka_df = (
        df
        .select(
            F.col("application_id").cast("string").alias("key"),
            F.to_json(F.struct("*")).alias("value"),
        )
        .filter(F.col("key").isNotNull())
        .filter(F.col("value").isNotNull())
    )

    jaas_config = (
        "org.apache.kafka.common.security.scram.ScramLoginModule required "
        f'username="{args.kafka_username}" '
        f'password="{args.kafka_password}";'
    )

    (
        kafka_df.write
        .format("kafka")
        .option("kafka.bootstrap.servers", args.kafka_bootstrap_servers)
        .option("topic", args.kafka_topic)
        .option("kafka.security.protocol", "SASL_SSL")
        .option("kafka.sasl.mechanism", "SCRAM-SHA-512")
        .option("kafka.sasl.jaas.config", jaas_config)
        .save()
    )

    print(f"Sent rows to Kafka topic: {args.kafka_topic}")
    spark.stop()


if __name__ == "__main__":
    main()