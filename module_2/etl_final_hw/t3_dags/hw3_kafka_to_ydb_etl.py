import datetime

from airflow import DAG
from airflow.models import Variable
from airflow.providers.yandex.operators.dataproc import DataprocCreatePysparkJobOperator


CLUSTER_ID = "c9q9415jcglmauogss19"

S3_BUCKET = "chumurovbucket"

KAFKA_BOOTSTRAP_SERVERS = "rc1b-0kdm902lnkoku6hs.mdb.yandexcloud.net:9091"
KAFKA_TOPIC = "loan-applications"
KAFKA_USERNAME = "user"
KAFKA_PASSWORD = Variable.get("KAFKA_PASSWORD")

YDB_ENDPOINT = "grpcs://ydb.serverless.yandexcloud.net:2135/?database=/ru-central1/b1g0919k5g23gtu2pc89/etn05vieg2t6qo30bm54"
YDB_DATABASE = "/ru-central1/b1g0919k5g23gtu2pc89/etn05vieg2t6qo30bm54"
YDB_TABLE = "loan_applications_flat"

KAFKA_PACKAGE = "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.2"


with DAG(
    dag_id="hw3_kafka_to_ydb_etl",
    description="HW3: S3 JSON -> Kafka -> PySpark flatten -> YDB",
    start_date=datetime.datetime(2026, 5, 1),
    schedule=None,
    catchup=False,
    max_active_runs=1,
    tags=["hw3", "kafka", "pyspark", "ydb"],
) as dag:

    send_json_to_kafka = DataprocCreatePysparkJobOperator(
        task_id="send_json_from_s3_to_kafka",
        cluster_id=CLUSTER_ID,
        main_python_file_uri=f"s3a://{S3_BUCKET}/hw3/jobs/kafka_json_producer.py",
        args=[
            f"--input-path=s3a://{S3_BUCKET}/test_json/loan_applications_20mb.json",
            f"--kafka-bootstrap-servers={KAFKA_BOOTSTRAP_SERVERS}",
            f"--kafka-topic={KAFKA_TOPIC}",
            f"--kafka-username={KAFKA_USERNAME}",
            f"--kafka-password={KAFKA_PASSWORD}",
            "--json-format=array",
        ],
        properties={
            "spark.jars.packages": KAFKA_PACKAGE,
        },
    )

    read_kafka_write_ydb = DataprocCreatePysparkJobOperator(
        task_id="read_kafka_flatten_write_ydb",
        cluster_id=CLUSTER_ID,
        main_python_file_uri=f"s3a://{S3_BUCKET}/hw3/jobs/kafka_to_ydb_flatten_consumer.py",
        args=[
            f"--kafka-bootstrap-servers={KAFKA_BOOTSTRAP_SERVERS}",
            f"--kafka-topic={KAFKA_TOPIC}",
            f"--kafka-username={KAFKA_USERNAME}",
            f"--kafka-password={KAFKA_PASSWORD}",
            f"--ydb-endpoint={YDB_ENDPOINT}",
            f"--ydb-database={YDB_DATABASE}",
            f"--ydb-table={YDB_TABLE}",
            f"--checkpoint-path=s3a://{S3_BUCKET}/hw3/checkpoints/loan_applications_flat",
        ],
        properties={
            "spark.jars.packages": KAFKA_PACKAGE,
            "spark.pyspark.python": "/opt/conda/bin/python",
            "spark.pyspark.driver.python": "/opt/conda/bin/python",
            "spark.executorEnv.USE_METADATA_CREDENTIALS": "1",
            "spark.yarn.appMasterEnv.USE_METADATA_CREDENTIALS": "1",
        },
    )

    send_json_to_kafka >> read_kafka_write_ydb