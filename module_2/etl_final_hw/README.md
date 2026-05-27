# Итоговое ДЗ. Модуль 4: ETL-процессы

Отчет по практической работе: загрузка и перенос данных в Yandex Cloud, автоматизация обработки через Apache Airflow и Yandex Data Processing, потоковая обработка Kafka-топика и визуализация результата в Yandex DataLens.

## Состав репозитория

- `csv/transactions.csv` - датасет для задания 1, около 76 МБ.
- `csv/credit_applications.csv` - датасет кредитных заявок для задания 2, около 51 МБ.
- `json/loan_applications_20mb.json` - JSON-датасет заявок для Kafka-пайплайна.
- `sql/` - DDL-скрипты для таблиц в YDB.
- `t2_dags/` - DAG и PySpark-job для обработки CSV в Yandex Data Processing.
- `t3_dags/` - DAG и PySpark-jobs для отправки JSON в Kafka и записи плоской таблицы в YDB.
- `скрины/` - подтверждающие скриншоты выполнения заданий.

## Задание 1. DataTransfer: YDB -> Object Storage

Для первого задания была создана таблица `transactions_v2` в Yandex Database. Структура таблицы сохранена в [sql/t1 transaction_v2_ddl.sql](sql/t1%20transaction_v2_ddl.sql).

```sql
CREATE TABLE transactions_v2 (
    transaction_id Utf8 NOT NULL,
    customer_id Utf8,
    transaction_timestamp Utf8,
    amount Double,
    merchant_category Utf8,
    is_fraud Int32,
    year Int32,
    month Int32,
    PRIMARY KEY (transaction_id)
);
```

Исходный CSV-файл был загружен в YDB. После загрузки проверено наличие записей в таблице.

![Загрузка данных в YDB](<скрины/t1 Загрузка данных в YDB.png>)

На скриншоте показан процесс загрузки подготовленного файла `transactions.csv` в таблицу `transactions_v2`.

![Результат в YDB](<скрины/t1 Результат в BD.png>)

Проверка результата в базе подтверждает, что данные доступны в YDB и могут быть использованы как источник для трансфера.

Далее был создан бакет Object Storage, который используется как целевое хранилище для DataTransfer.

![Бакет Object Storage](<скрины/t1 бакет.png>)

После подготовки источника и приемника был настроен трансфер из Managed Service for YDB в Object Storage.

![Настройка трансфера](<скрины/t1 трансфер.png>)

Трансфер был запущен и завершился успешно. В бакете появились выгруженные данные.

![Результат трансфера](<скрины/t1 результат трансфера.png>)

Итог задания 1: данные из YDB перенесены в Object Storage через Yandex DataTransfer, DDL-скрипт сохранен в репозитории.

## Задание 2. Airflow + Yandex Data Processing

Во втором задании был подготовлен процесс обработки файла `credit_applications.csv`. DDL для таблицы кредитных заявок сохранен в [sql/credit_applications_ddl.sql](sql/credit_applications_ddl.sql).

Обработка автоматизирована через Apache Airflow. DAG находится в [t2_dags/hw2_dataproc_credit_etl.py](t2_dags/hw2_dataproc_credit_etl.py) и выполняет три шага:

1. Создает временный кластер Yandex Data Processing.
2. Запускает PySpark-задание.
3. Удаляет кластер после выполнения.

![Поднятый Airflow](<скрины/t2 поднятый airflow.png>)

На скриншоте показан запущенный Apache Airflow, через который выполнялось управление ETL-процессом.

PySpark-скрипт находится в [t2_dags/process_credit_applications.py](t2_dags/process_credit_applications.py). В нем выполняются:

- чтение CSV из Object Storage;
- приведение типов для дат, сумм, скоринга и флагов;
- фильтрация некорректных записей;
- расчет `approved_ratio`;
- сохранение очищенного слоя в parquet;
- построение витрин по регионам, дням и продуктам.

Сформированные выходные наборы:

- `credit_applications_clean` - очищенный слой, партиционированный по `event_date`;
- `mart_credit_by_region` - агрегаты по региону, уровню риска и статусу решения;
- `mart_credit_by_day` - дневная динамика заявок;
- `mart_credit_by_product` - показатели по продуктам и каналам.

![Отработавшие DAG-и](<скрины/t2 отработали даги.png>)

DAG отработал успешно: кластер был создан, PySpark-job выполнен, затем временный кластер удален.

![Готовые витрины](<скрины/t2 готовые витрины.png>)

На скриншоте показаны подготовленные parquet-витрины в Object Storage.

Итог задания 2: построен автоматизированный batch ETL-процесс в Airflow с запуском PySpark на Yandex Data Processing.

## Задание 3. Kafka + PySpark + YDB

Для третьего задания был настроен потоковый сценарий: JSON-файл из Object Storage отправляется в Kafka-топик, затем PySpark-задание читает сообщения из Kafka, разворачивает вложенную JSON-структуру в плоский вид и пишет результат в YDB.

DDL целевой таблицы сохранен в [sql/t3_ddl.sql](sql/t3_ddl.sql). Таблица `loan_applications_flat` содержит бизнес-поля заявки и технические Kafka-поля:

- `application_id`, `customer_id`, `region`;
- параметры кредита: `loan_amount`, `term_months`;
- скоринг: `scoring_score`, `risk_level`;
- данные первого документа и количество документов;
- `decision_status`, `submitted_at`;
- `kafka_topic`, `kafka_partition`, `kafka_offset`, `processed_at`.

Kafka-кластер и топик `loan-applications` были созданы в Yandex Cloud.

![Kafka и топик](<скрины/t3 кафка с топиком созданы.png>)

DAG третьего задания находится в [t3_dags/hw3_kafka_to_ydb_etl.py](t3_dags/hw3_kafka_to_ydb_etl.py). Он запускает два PySpark-задания:

1. [t3_dags/kafka_json_producer.py](t3_dags/kafka_json_producer.py) - читает JSON из Object Storage и отправляет записи в Kafka.
2. [t3_dags/kafka_to_ydb_flatten_consumer.py](t3_dags/kafka_to_ydb_flatten_consumer.py) - читает Kafka-топик, парсит JSON, приводит данные к плоскому виду и записывает их в YDB через bulk upsert.

![DAG задания 3](<скрины/t3 даг отработал.png>)

DAG успешно выполнил оба шага: отправку данных в Kafka и последующую обработку сообщений.

![Job отработали](<скрины/t3 job отработали.png>)

На уровне Data Processing видно, что PySpark jobs завершились без ошибки.

![Данные в YDB](<скрины/t3 данные в ydb.png>)

После выполнения пайплайна данные появились в таблице `loan_applications_flat` в YDB.

Итог задания 3: реализован Kafka-пайплайн с чтением JSON, передачей сообщений через Kafka, flatten-преобразованием и загрузкой результата в YDB.

## Задание 4. Визуализация в DataLens

Для финального задания был собран дашборд в Yandex DataLens. Визуализация построена на подготовленных данных и показывает основные метрики по заявкам и результатам обработки.

![Дашборд DataLens](<скрины/t4 дашборд.png>)

На дашборде представлены агрегированные показатели, которые позволяют анализировать данные после выполнения ETL-процессов: динамику заявок, распределение по статусам, рискам, регионам и продуктам.

Итог задания 4: построена визуализация в DataLens на основе результатов обработки данных.

## Общий итог

В рамках работы были выполнены все основные пункты задания:

- подготовлены исходные данные нужного объема;
- создана таблица в YDB и выполнен трансфер в Object Storage;
- реализован batch ETL-процесс через Airflow и Yandex Data Processing;
- подготовлены витрины в parquet-формате;
- настроен Kafka-топик и PySpark-пайплайн для обработки JSON-сообщений;
- результат потоковой обработки записан в YDB;
- построен дашборд в DataLens;
- SQL-скрипты и код DAG/PySpark-заданий сохранены в репозитории.

