import os
import pytest
import asyncio

# Установить переменную окружения перед импортом модулей приложения
os.environ["DB_FILE"] = "./test_shorturl.db"

from shorturl_app.database import init_db

@pytest.fixture(scope="function", autouse=True)
async def setup_db():
    # Обеспечить чистое состояние (удалить старую тестовую БД, если она есть)
    if os.path.exists("./test_shorturl.db"):
        os.remove("./test_shorturl.db")
        
    await init_db()
    yield
    # Очистка: удалить файл тестовой БД
    if os.path.exists("./test_shorturl.db"):
        os.remove("./test_shorturl.db")
