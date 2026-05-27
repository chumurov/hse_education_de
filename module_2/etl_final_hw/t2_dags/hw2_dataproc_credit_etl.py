import datetime

from airflow import DAG
from airflow.providers.yandex.operators.dataproc import (
    DataprocCreateClusterOperator,
    DataprocCreatePysparkJobOperator,
    DataprocDeleteClusterOperator,
)


FOLDER_ID = "b1gd1ukq6vrlepbkcdbf"
SUBNET_ID = "e2len4lj0gl7imq95pei"
SERVICE_ACCOUNT_ID = "ajet9d8fanpl2nv2vnb2"
ZONE = "ru-central1-b"

S3_BUCKET = "chumurovbucket"
MAIN_PYTHON_FILE_URI = "s3a://chumurovbucket/hw2/jobs/process_credit_applications.py"

CLUSTER_NAME = "hw2-dp-credit"

SSH_PUBLIC_KEY = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIOh4NiIfoD/FxtmC9JkCeI/RIFyWza7EEbutk2qIYaBD chumurov.nikita@gmail.com"


with DAG(
    dag_id="hw2_dataproc_credit_applications_etl",
    description="HW2: create Data Processing cluster, run PySpark ETL, delete cluster",
    start_date=datetime.datetime(2026, 5, 1),
    schedule=None,
    catchup=False,
    max_active_runs=1,
    tags=["hw2", "dataproc", "pyspark", "etl"],
) as dag:

    create_cluster = DataprocCreateClusterOperator(
        task_id="create_dataproc_cluster",
        folder_id=FOLDER_ID,
        cluster_name=CLUSTER_NAME,
        cluster_description="Temporary Data Processing cluster for HW2 PySpark ETL",
        cluster_image_version="2.1",
        subnet_id=SUBNET_ID,
        service_account_id=SERVICE_ACCOUNT_ID,
        s3_bucket=S3_BUCKET,
        zone=ZONE,
        services=("HDFS", "YARN", "SPARK"),
        ssh_public_keys=[SSH_PUBLIC_KEY],
        masternode_resource_preset="s2.small",
        masternode_disk_size=40,
        masternode_disk_type="network-hdd",
        datanode_resource_preset="s2.small",
        datanode_disk_size=40,
        datanode_disk_type="network-hdd",
        datanode_count=1,
    )

    run_pyspark_job = DataprocCreatePysparkJobOperator(
        task_id="run_credit_applications_pyspark_job",
        cluster_id="{{ ti.xcom_pull(task_ids='create_dataproc_cluster', key='cluster_id') }}",
        main_python_file_uri=MAIN_PYTHON_FILE_URI,
        trigger_rule="all_done",
    )

    delete_cluster = DataprocDeleteClusterOperator(
        task_id="delete_dataproc_cluster",
        cluster_id="{{ ti.xcom_pull(task_ids='create_dataproc_cluster', key='cluster_id') }}",
        trigger_rule="all_done",
    )

    create_cluster >> run_pyspark_job >> delete_cluster