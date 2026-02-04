import os
import json
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from airflow import DAG
from airflow.decorators import dag, task
from dotenv import load_dotenv
import psycopg2

# Путь к файлу с кредами
DOTENV_PATH = '/opt/airflow/dags/.env'
FILE_PATH_XML = '/opt/airflow/dags/file/nutrition.xml'
FILE_PATH_JSON = '/opt/airflow/dags/file/pets-data.json'

def get_db_connection():
    load_dotenv(DOTENV_PATH)
    host = os.getenv("PG_HOST")
    # Если мы в докере и хост localhost, меняем на host.docker.internal
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
    dag_id='data_parsing_ingestion_v1',
    schedule=timedelta(days=1),
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['airflow3', 'parsing'],
)
def ingestion_dag():

    @task
    def create_tables():
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Таблица для питания
        cur.execute("""
            CREATE TABLE IF NOT EXISTS nutrition_data (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255),
                mfr VARCHAR(255),
                calories_total NUMERIC(10, 2),
                protein NUMERIC(10, 2),
                fat NUMERIC(10, 2)
            );
        """)
        
        # Таблица для питомцев
        cur.execute("""
            CREATE TABLE IF NOT EXISTS pets_data (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255),
                species VARCHAR(255),
                birth_year INT,
                photo TEXT,
                fav_foods TEXT[]
            );
        """)
        
        conn.commit()
        cur.close()
        conn.close()

    @task
    def parse_and_load_xml():
        tree = ET.parse(FILE_PATH_XML)
        root = tree.getroot()
        
        foods = []
        for food in root.findall('food'):
            name = food.find('name').text if food.find('name') is not None else None
            mfr = food.find('mfr').text if food.find('mfr') is not None else None
            
            calories_elem = food.find('calories')
            calories_total = float(calories_elem.get('total')) if calories_elem is not None else 0.0
            
            protein = float(food.find('protein').text) if food.find('protein') is not None else 0.0
            fat = float(food.find('total-fat').text) if food.find('total-fat') is not None else 0.0
            
            foods.append((name, mfr, calories_total, protein, fat))
            
        conn = get_db_connection()
        cur = conn.cursor()
        cur.executemany(
            "INSERT INTO nutrition_data (name, mfr, calories_total, protein, fat) VALUES (%s, %s, %s, %s, %s)",
            foods
        )
        conn.commit()
        cur.close()
        conn.close()
        return len(foods)

    @task
    def parse_and_load_json():
        with open(FILE_PATH_JSON, 'r') as f:
            data = json.load(f)
            
        pets = []
        for pet in data.get('pets', []):
            pets.append((
                pet.get('name'),
                pet.get('species'),
                pet.get('birthYear'),
                pet.get('photo'),
                pet.get('favFoods')
            ))
            
        conn = get_db_connection()
        cur = conn.cursor()
        cur.executemany(
            "INSERT INTO pets_data (name, species, birth_year, photo, fav_foods) VALUES (%s, %s, %s, %s, %s)",
            pets
        )
        conn.commit()
        cur.close()
        conn.close()
        return len(pets)

    # Установка зависимостей
    create_tables_task = create_tables()
    xml_task = parse_and_load_xml()
    json_task = parse_and_load_json()
    
    create_tables_task >> [xml_task, json_task]

# Инициализация DAG
data_ingestion_dag = ingestion_dag()
