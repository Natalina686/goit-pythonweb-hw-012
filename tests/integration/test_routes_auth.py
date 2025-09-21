import pytest
from httpx import AsyncClient
from asgi_lifespan import LifespanManager
from src.main import app

@pytest.mark.asyncio
async def test_register_and_login():

    async with LifespanManager(app):
        async with AsyncClient(app=app, base_url="http://test") as client:
            
            register_data = {"email": "test@example.com", "password": "123456"}
            response = await client.post("/auth/register", json=register_data)
            assert response.status_code == 201
            assert "id" in response.json()

           
            login_data = {"username": "test@example.com", "password": "123456"}
            response = await client.post("/auth/login", data=login_data)
            assert response.status_code == 200
            assert "access_token" in response.json()
            assert response.json()["token_type"] == "bearer"
