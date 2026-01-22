import os
import pytest
import asyncio

# Установить переменную окружения перед импортом модулей приложения
os.environ["DB_FILE"] = "./test_todo.db"

from todo_app.database import init_db

@pytest.fixture(scope="function", autouse=True)
async def setup_db():
    # Обеспечить чистое состояние (удалить старую тестовую БД, если она есть)
    if os.path.exists("./test_todo.db"):
        os.remove("./test_todo.db")
        
    await init_db()
    yield
    # Очистка: удалить файл тестовой БД
    if os.path.exists("./test_todo.db"):
        os.remove("./test_todo.db")
