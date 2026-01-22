import pytest
from httpx import AsyncClient, ASGITransport

try:
    from shorturl_app.main import app
except ImportError:
    app = None

@pytest.mark.asyncio
async def test_create_short_url():
    if app is None:
        pytest.fail("App not initialized")
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/urls/", json={"url": "https://example.com"})
    
    assert response.status_code == 201
    data = response.json()
    assert data["url"] == "https://example.com/"
    assert "id" in data
    assert len(data["id"]) == 8

@pytest.mark.asyncio
async def test_redirect_url():
    if app is None:
        pytest.fail("App not initialized")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Создать
        create_response = await ac.post("/urls/", json={"url": "https://example.com"})
        short_id = create_response.json()["id"]
        
        # Редирект
        response = await ac.get(f"/{short_id}")
    
    assert response.status_code == 307
    assert response.headers["location"] == "https://example.com/"
