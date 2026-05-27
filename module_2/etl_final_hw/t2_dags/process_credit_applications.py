from pyspark.sql import SparkSession
from pyspark.sql import functions as F


INPUT_PATH = "s3a://chumurovbucket/test_csv/credit_applications.csv"

CLEAN_OUTPUT_PATH = "s3a://chumurovbucket/hw2/output/credit_applications_clean"
REGION_MART_OUTPUT_PATH = "s3a://chumurovbucket/hw2/output/mart_credit_by_region"
DAY_MART_OUTPUT_PATH = "s3a://chumurovbucket/hw2/output/mart_credit_by_day"
PRODUCT_MART_OUTPUT_PATH = "s3a://chumurovbucket/hw2/output/mart_credit_by_product"


def main() -> None:
    spark = (
        SparkSession.builder
        .appName("hw2_credit_applications_etl")
        .getOrCreate()
    )

    raw_df = (
        spark.read
        .option("header", "true")
        .option("inferSchema", "false")
        .csv(INPUT_PATH)
    )

    clean_df = (
        raw_df
        .withColumn("event_time", F.to_timestamp("event_time"))
        .withColumn("event_date", F.to_date("event_time"))
        .withColumn("customer_id", F.col("customer_id").cast("long"))
        .withColumn("requested_amount", F.col("requested_amount").cast("double"))
        .withColumn("term_months", F.col("term_months").cast("int"))
        .withColumn("credit_score", F.col("credit_score").cast("int"))
        .withColumn("approved_amount", F.col("approved_amount").cast("double"))
        .withColumn("processing_time_sec", F.col("processing_time_sec").cast("int"))
        .withColumn(
            "employee_review_flag",
            F.when(F.upper(F.col("employee_review_flag")).isin("Y", "YES", "TRUE", "1"), F.lit(True))
             .when(F.upper(F.col("employee_review_flag")).isin("N", "NO", "FALSE", "0"), F.lit(False))
             .otherwise(F.lit(None))
        )
        .withColumn(
            "approved_ratio",
            F.when(
                F.col("requested_amount") > 0,
                F.col("approved_amount") / F.col("requested_amount")
            ).otherwise(F.lit(None))
        )
        .withColumn("processing_date", F.current_date())
        .filter(F.col("application_id").isNotNull())
        .filter(F.col("event_time").isNotNull())
        .filter(F.col("customer_id").isNotNull())
        .filter(F.col("requested_amount") > 0)
        .filter(F.col("term_months") > 0)
        .filter(F.col("credit_score").between(0, 1000))
    )

    (
        clean_df
        .write
        .mode("overwrite")
        .partitionBy("event_date")
        .parquet(CLEAN_OUTPUT_PATH)
    )

    region_mart_df = (
        clean_df
        .groupBy("region_code", "risk_level", "decision_status")
        .agg(
            F.count("*").alias("applications_cnt"),
            F.countDistinct("customer_id").alias("customers_cnt"),
            F.sum("requested_amount").alias("requested_amount_sum"),
            F.sum("approved_amount").alias("approved_amount_sum"),
            F.avg("requested_amount").alias("avg_requested_amount"),
            F.avg("approved_amount").alias("avg_approved_amount"),
            F.avg("credit_score").alias("avg_credit_score"),
            F.avg("processing_time_sec").alias("avg_processing_time_sec"),
            F.avg("approved_ratio").alias("avg_approved_ratio"),
        )
    )

    (
        region_mart_df
        .write
        .mode("overwrite")
        .parquet(REGION_MART_OUTPUT_PATH)
    )

    day_mart_df = (
        clean_df
        .groupBy("event_date", "decision_status")
        .agg(
            F.count("*").alias("applications_cnt"),
            F.sum("requested_amount").alias("requested_amount_sum"),
            F.sum("approved_amount").alias("approved_amount_sum"),
            F.avg("credit_score").alias("avg_credit_score"),
        )
    )

    (
        day_mart_df
        .write
        .mode("overwrite")
        .parquet(DAY_MART_OUTPUT_PATH)
    )

    product_mart_df = (
        clean_df
        .groupBy("product_type", "channel", "decision_status")
        .agg(
            F.count("*").alias("applications_cnt"),
            F.sum("requested_amount").alias("requested_amount_sum"),
            F.sum("approved_amount").alias("approved_amount_sum"),
            F.avg("processing_time_sec").alias("avg_processing_time_sec"),
        )
    )

    (
        product_mart_df
        .write
        .mode("overwrite")
        .parquet(PRODUCT_MART_OUTPUT_PATH)
    )

    spark.stop()


if __name__ == "__main__":
    main()