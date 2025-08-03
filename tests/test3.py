import pymysql
import os
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())
connection = pymysql.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)

with connection.cursor() as cursor:
    cursor.execute("SELECT DATABASE();")
    current_db = cursor.fetchone()
    print(f"✅ Подключено к базе: {current_db[0]}")
