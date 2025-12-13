from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import RedirectResponse
import aiosqlite
from nanoid import generate

from shorturl_app.database import init_db, get_db
from shorturl_app.models import URLItem, URLCreate

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(lifespan=lifespan)

@app.post("/urls/", response_model=URLItem, status_code=201)
async def create_short_url(url: URLCreate, db: aiosqlite.Connection = Depends(get_db)):
    # Генерируем уникальный идентификатор
    short_id = generate(size=8)
    
    await db.execute(
        "INSERT INTO urls (id, url) VALUES (?, ?)",
        (short_id, str(url.url)),
    )
    await db.commit()
    
    return URLItem(id=short_id, url=url.url)

@app.get("/{short_id}")
async def redirect_to_url(short_id: str, db: aiosqlite.Connection = Depends(get_db)):
    async with db.execute("SELECT url FROM urls WHERE id = ?", (short_id,)) as cursor:
        row = await cursor.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="URL not found")
        
        return RedirectResponse(url=row["url"])
