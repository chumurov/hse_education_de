import pytest
from httpx import AsyncClient, ASGITransport

# Ожидается, что импорт может не выполниться изначально
try:
    from todo_app.main import app
except ImportError:
    app = None

@pytest.mark.asyncio
async def test_create_task():
    if app is None:
        pytest.fail("App not initialized")
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/tasks/", json={"title": "Test Task", "description": "Test Description"})
    
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Task"
    assert "id" in data
    assert data["completed"] is False

@pytest.mark.asyncio
async def test_read_tasks():
    if app is None:
        pytest.fail("App not initialized")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Сначала создаём задачу
        await ac.post("/tasks/", json={"title": "Task 1"})
        
        response = await ac.get("/tasks/")
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0
