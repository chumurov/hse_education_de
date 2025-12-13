import os
from pathlib import Path
import aiosqlite

DB_FILE = os.getenv("DB_FILE", "/app/data/shorturl.db")

async def get_db():
    Path(DB_FILE).parent.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(DB_FILE) as db:
        db.row_factory = aiosqlite.Row
        yield db

async def init_db():
    Path(DB_FILE).parent.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS urls (
                id TEXT PRIMARY KEY,
                url TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                clicks INTEGER DEFAULT 0
            )
        """)
        await db.commit()
