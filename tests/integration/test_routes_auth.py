import pytest
from httpx import AsyncClient
from src.main import app

@pytest.mark.asyncio
async def test_register_and_login():
    async with AsyncClient(app=app, base_url="http://test") as ac:
    
        resp = await ac.post("/auth/register", json={"email":"b@test.com","password":"pass123"})
        assert resp.status_code == 201

        resp = await ac.post("/auth/login", data={"username":"b@test.com","password":"pass123"})
        assert resp.status_code == 200
        assert "access_token" in resp.json()
