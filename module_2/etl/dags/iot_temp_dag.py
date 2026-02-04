import os
import csv
from datetime import datetime, timedelta
from airflow import DAG
from airflow.decorators import dag, task
from dotenv import load_dotenv
import psycopg2

# Пути к файлам внутри контейнера Airflow
DOTENV_PATH = '/opt/airflow/dags/.env'
CSV_FILE_PATH = '/opt/airflow/dags/file/IOT-temp.csv'

def get_db_connection():
    load_dotenv(DOTENV_PATH)
    host = os.getenv("PG_HOST")
    # Если запуск в докере, localhost базы данных не сработает (это сам контейнер)
    # Используем host.docker.internal для доступа к хосту
    if host == 'localhost' and os.path.exists('/.dockerenv'):
        host = 'host.docker.internal'
        
    return psycopg2.connect(
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        database=os.getenv("PG_DB"),
        host=host,
        port=os.getenv("PG_PORT")
    )

@dag(
    dag_id='iot_temp_data_ingestion',
    schedule=timedelta(days=1),
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['iot', 'csv', 'ingestion'],
)
def iot_data_dag():

    @task
    def create_iot_table():
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS iot_temp_data (
                id TEXT PRIMARY KEY,
                room_id TEXT,
                noted_date TIMESTAMP,
                temp INTEGER,
                out_in TEXT
            );
        """)
        
        conn.commit()
        cur.close()
        conn.close()

    @task
    def load_iot_data():
        if not os.path.exists(CSV_FILE_PATH):
            raise FileNotFoundError(f"CSV файл не найден: {CSV_FILE_PATH}")
            
        data_to_insert = []
        with open(CSV_FILE_PATH, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Формат даты в файле: 08-12-2018 09:30 (DD-MM-YYYY HH:MM)
                try:
                    noted_date = datetime.strptime(row['noted_date'], '%d-%m-%Y %H:%M')
                except ValueError:
                    # Если формат отличается, передаем как есть (Postgres попробует распарсить сам)
                    noted_date = row['noted_date']
                
                data_to_insert.append((
                    row['id'],
                    row['room_id/id'],
                    noted_date,
                    int(row['temp']),
                    row['out/in']
                ))

        conn = get_db_connection()
        cur = conn.cursor()
        
        # Используем INSERT ON CONFLICT DO NOTHING, чтобы избежать ошибок при повторном запуске
        query = """
            INSERT INTO iot_temp_data (id, room_id, noted_date, temp, out_in)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        """
        
        cur.executemany(query, data_to_insert)
        
        inserted_count = cur.rowcount
        conn.commit()
        cur.close()
        conn.close()
        
        print(f"Успешно обработано {len(data_to_insert)} строк.")
        return len(data_to_insert)

    @task
    def create_analytical_tables():
        conn = get_db_connection()
        cur = conn.cursor()
        
        # 1. Запрос на ТОП-5 дат с макс. средней темп. и 1 дату с мин. средней темп.
        cur.execute("DROP TABLE IF EXISTS iot_temp_min_max_avg;")
        cur.execute("""
            CREATE TABLE iot_temp_min_max_avg AS
            SELECT *
            FROM (
                SELECT CAST(noted_date AS DATE) noted_date, AVG(temp) avg_temp, 'max' as type
                FROM iot_temp_data itd 
                GROUP BY CAST(noted_date AS DATE)
                ORDER BY AVG(temp) DESC
                LIMIT 5
            ) t
            UNION ALL
            SELECT *
            FROM (
                SELECT CAST(noted_date AS DATE) noted_date, AVG(temp) avg_temp, 'min' as type
                FROM iot_temp_data itd 
                GROUP BY CAST(noted_date AS DATE)
                ORDER BY AVG(temp) ASC
                LIMIT 1
            ) t;
        """)

        # 2. Только замеры внутри помещения
        cur.execute("DROP TABLE IF EXISTS iot_temp_indoor;")
        cur.execute("""
            CREATE TABLE iot_temp_indoor AS
            SELECT *
            FROM iot_temp_data itd 
            WHERE itd.out_in = 'In';
        """)

        # 3. Приведение дат к формату DATE (без времени)
        cur.execute("DROP TABLE IF EXISTS iot_temp_by_date;")
        cur.execute("""
            CREATE TABLE iot_temp_by_date AS
            SELECT id, room_id, CAST(noted_date AS DATE) noted_date, "temp", out_in
            FROM iot_temp_data itd;
        """)

        # 4. Удаление выбросов через перцентили 0.05 и 0.95
        cur.execute("DROP TABLE IF EXISTS iot_temp_filtered;")
        cur.execute("""
            CREATE TABLE iot_temp_filtered AS
            WITH bounds AS (
                SELECT
                    percentile_cont(0.05) WITHIN GROUP (ORDER BY temp) AS p05,
                    percentile_cont(0.95) WITHIN GROUP (ORDER BY temp) AS p95
                FROM iot_temp_data
            )
            SELECT t.*
            FROM iot_temp_data t
            CROSS JOIN bounds b
            WHERE t.temp >= b.p05 
              AND t.temp <= b.p95;
        """)
        
        conn.commit()
        cur.close()
        conn.close()
        print("Аналитические таблицы успешно созданы.")

    @task
    def create_analytical_tables_last_10_days():
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("DROP TABLE IF EXISTS iot_temp_min_max_avg_last_10_days;")
        cur.execute("""
            CREATE TABLE iot_temp_min_max_avg_last_10_days AS
            WITH max_date AS (
                SELECT MAX(noted_date) AS max_date
                FROM iot_temp_data
            ),
            base AS (
                SELECT *
                FROM iot_temp_data
                WHERE noted_date >= (SELECT max_date - INTERVAL '10 days' FROM max_date)
            )
            SELECT *
            FROM (
                SELECT CAST(noted_date AS DATE) noted_date, AVG(temp) avg_temp, 'max' as type
                FROM base
                GROUP BY CAST(noted_date AS DATE)
                ORDER BY AVG(temp) DESC
                LIMIT 5
            ) t
            UNION ALL
            SELECT *
            FROM (
                SELECT CAST(noted_date AS DATE) noted_date, AVG(temp) avg_temp, 'min' as type
                FROM base
                GROUP BY CAST(noted_date AS DATE)
                ORDER BY AVG(temp) ASC
                LIMIT 1
            ) t;
        """)

        cur.execute("DROP TABLE IF EXISTS iot_temp_indoor_last_10_days;")
        cur.execute("""
            CREATE TABLE iot_temp_indoor_last_10_days AS
            WITH max_date AS (
                SELECT MAX(noted_date) AS max_date
                FROM iot_temp_data
            )
            SELECT *
            FROM iot_temp_data
            WHERE out_in = 'In'
              AND noted_date >= (SELECT max_date - INTERVAL '10 days' FROM max_date);
        """)

        cur.execute("DROP TABLE IF EXISTS iot_temp_by_date_last_10_days;")
        cur.execute("""
            CREATE TABLE iot_temp_by_date_last_10_days AS
            WITH max_date AS (
                SELECT MAX(noted_date) AS max_date
                FROM iot_temp_data
            )
            SELECT id, room_id, CAST(noted_date AS DATE) noted_date, "temp", out_in
            FROM iot_temp_data
            WHERE noted_date >= (SELECT max_date - INTERVAL '10 days' FROM max_date);
        """)

        cur.execute("DROP TABLE IF EXISTS iot_temp_filtered_last_10_days;")
        cur.execute("""
            CREATE TABLE iot_temp_filtered_last_10_days AS
            WITH max_date AS (
                SELECT MAX(noted_date) AS max_date
                FROM iot_temp_data
            ),
            base AS (
                SELECT *
                FROM iot_temp_data
                WHERE noted_date >= (SELECT max_date - INTERVAL '10 days' FROM max_date)
            ),
            bounds AS (
                SELECT
                    percentile_cont(0.05) WITHIN GROUP (ORDER BY temp) AS p05,
                    percentile_cont(0.95) WITHIN GROUP (ORDER BY temp) AS p95
                FROM base
            )
            SELECT t.*
            FROM base t
            CROSS JOIN bounds b
            WHERE t.temp >= b.p05
              AND t.temp <= b.p95;
        """)

        conn.commit()
        cur.close()
        conn.close()
        print("Аналитические таблицы за последние 10 дней успешно созданы.")

    # Определение последовательности
    create_iot_table() >> load_iot_data() >> create_analytical_tables() >> create_analytical_tables_last_10_days()

# Регистрация DAG
iot_temp_dag = iot_data_dag()
