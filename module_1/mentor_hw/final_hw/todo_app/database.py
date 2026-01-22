import os
from pathlib import Path
import aiosqlite

# По умолчанию используем локальную папку данных, если приложение не запущено в Docker (простая эвристика или переменная окружения).
# Но в требованиях указана папка /app/data/todo.db.
# Используем переменную окружения для возможности локального переопределения; по умолчанию /app/data/todo.db
DB_FILE = os.getenv("DB_FILE", "/app/data/todo.db")

async def get_db():
    # Убедиться, что директория для файла базы данных существует
    Path(DB_FILE).parent.mkdir(parents=True, exist_ok=True)
    
    async with aiosqlite.connect(DB_FILE) as db:
        db.row_factory = aiosqlite.Row
        yield db

async def init_db():
    Path(DB_FILE).parent.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                completed BOOLEAN DEFAULT 0
            )
        """)
        await db.commit()
