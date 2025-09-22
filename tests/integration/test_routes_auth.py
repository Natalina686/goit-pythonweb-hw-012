import pytest
from httpx import AsyncClient
from asgi_lifespan import LifespanManager
from src.main import app
from src.db import get_db
from src import crud


@pytest.fixture(autouse=True)
def clear_users_table():
    db = next(get_db())
    db.query(crud.models.User).delete()
    db.commit()
    yield
    db.rollback()


@pytest.mark.anyio("asyncio")
async def test_register_and_login():
    async with LifespanManager(app):
        async with AsyncClient(app=app, base_url="http://test") as client:
            
            
            register_data = {"email": "test@example.com", "password": "123456", "full_name": "Test User"}
            response = await client.post("/auth/register", json=register_data)
            assert response.status_code == 201
            user_data = response.json()
            assert "id" in user_data
            assert user_data["email"] == "test@example.com"

            
            response_dup = await client.post("/auth/register", json=register_data)
            assert response_dup.status_code == 409 

            
            login_data = {"username": "test@example.com", "password": "123456"}
            response = await client.post("/auth/login", data=login_data)
            assert response.status_code == 200
            token_data = response.json()
            assert "access_token" in token_data
            assert token_data["token_type"] == "bearer"

            
            access_token = token_data["access_token"]
            assert access_token.count(".") == 2

            
            wrong_login = {"username": "test@example.com", "password": "wrongpass"}
            response_wrong = await client.post("/auth/login", data=wrong_login)
            assert response_wrong.status_code == 401

            
            nonexistent_login = {"username": "noone@test.com", "password": "123456"}
            response_nonexistent = await client.post("/auth/login", data=nonexistent_login)
            assert response_nonexistent.status_code == 401
