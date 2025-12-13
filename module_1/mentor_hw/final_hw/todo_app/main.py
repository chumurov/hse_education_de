from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from typing import List
import aiosqlite

from todo_app.database import init_db, get_db
from todo_app.models import Task, TaskCreate

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(lifespan=lifespan)

@app.post("/tasks/", response_model=Task, status_code=201)
async def create_task(task: TaskCreate, db: aiosqlite.Connection = Depends(get_db)):
    cursor = await db.execute(
        "INSERT INTO tasks (title, description, completed) VALUES (?, ?, ?)",
        (task.title, task.description, task.completed),
    )
    await db.commit()
    task_id = cursor.lastrowid
    return Task(id=task_id, **task.model_dump())

@app.get("/tasks/", response_model=List[Task])
async def read_tasks(db: aiosqlite.Connection = Depends(get_db)):
    async with db.execute("SELECT id, title, description, completed FROM tasks") as cursor:
        rows = await cursor.fetchall()
        return [Task(id=row["id"], title=row["title"], description=row["description"], completed=bool(row["completed"])) for row in rows]

@app.get("/tasks/{task_id}", response_model=Task)
async def read_task(task_id: int, db: aiosqlite.Connection = Depends(get_db)):
    async with db.execute("SELECT id, title, description, completed FROM tasks WHERE id = ?", (task_id,)) as cursor:
        row = await cursor.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Task not found")
        return Task(id=row["id"], title=row["title"], description=row["description"], completed=bool(row["completed"]))

@app.put("/tasks/{task_id}", response_model=Task)
async def update_task(task_id: int, task: TaskCreate, db: aiosqlite.Connection = Depends(get_db)):
    # Проверяем, существует ли задача
    async with db.execute("SELECT id FROM tasks WHERE id = ?", (task_id,)) as cursor:
        if await cursor.fetchone() is None:
            raise HTTPException(status_code=404, detail="Task not found")
            
    await db.execute(
        "UPDATE tasks SET title = ?, description = ?, completed = ? WHERE id = ?",
        (task.title, task.description, task.completed, task_id),
    )
    await db.commit()
    return Task(id=task_id, **task.model_dump())

@app.delete("/tasks/{task_id}", status_code=204)
async def delete_task(task_id: int, db: aiosqlite.Connection = Depends(get_db)):
    async with db.execute("SELECT id FROM tasks WHERE id = ?", (task_id,)) as cursor:
        if await cursor.fetchone() is None:
            raise HTTPException(status_code=404, detail="Task not found")
            
    await db.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    await db.commit()

