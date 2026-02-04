# Отчет о выполнении дз 1 по ETL

Даг написан лежит по пути dags/data_ingestion_dag.py
Можно увидеть успешное выполенение по пути

<img src="./screenshot/airflow.png" width="1000" alt="Скрин">

Результат

<img src="./screenshot/table1.png" width="1000" alt="Скрин">
<img src="./screenshot/table2.png" width="1000" alt="Скрин">


# Отчет о выполнении дз 2 по ETL

Даг написан лежит по пути dags/iot_temp_dag.py
Можно увидеть успешное выполенение по пути

<img src="./screenshot/dag_2.png" width="500" alt="Скрин">


вычислите 5 самых жарких и самых холодных дней за год;


<img src="./screenshot/max_min.png" width="500" alt="Скрин">



отфильтруйте out/in = in;




поле noted_date переведите в формат ‘yyyy-MM-dd’ с типом данных date;


<img src="./screenshot/dz2_date.png" width="500" alt="Скрин">



очистите температуру по 5-му и 95-му процентилю.


<img src="./screenshot/dz2_5-95.png" width="500" alt="Скрин">

# Отчет о выполнении дз 3 по ETL

Я добавил новую таску в даг dags/iot_temp_dag.py

reate_analytical_tables_last_10_days()

вот результат созданные таблицы

<img src="./screenshot/dz_3.png" width="500" alt="Скрин">
