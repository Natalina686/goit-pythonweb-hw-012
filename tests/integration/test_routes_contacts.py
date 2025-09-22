import pytest
import uuid
from httpx import AsyncClient
from asgi_lifespan import LifespanManager
from src.main import app

@pytest.mark.anyio
async def test_crud_contacts():
    async with LifespanManager(app):
        async with AsyncClient(app=app, base_url="http://test") as ac:

           
            email = f"{uuid.uuid4().hex[:6]}@test.com"

            register_resp = await ac.post("/auth/register", json={
                "email": email,
                "password": "pass123"
            })
            assert register_resp.status_code == 201

            login_resp = await ac.post("/auth/login", data={
                "username": email,
                "password": "pass123"
            })
            assert login_resp.status_code == 200
            token = login_resp.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}

            
            contact_data = {
                "first_name": "John",
                "last_name": "Doe",
                "email": "john@test.com",
                "phone": "123456",
                "birthday": "2000-01-01"
            }
            resp = await ac.post("/contacts/", json=contact_data, headers=headers)
            assert resp.status_code == 201
            contact_id = resp.json()["id"]

            
            resp = await ac.get(f"/contacts/{contact_id}", headers=headers)
            assert resp.status_code == 200
            assert resp.json()["first_name"] == "John"

            
            resp = await ac.put(f"/contacts/{contact_id}", json={"first_name": "Jane"}, headers=headers)
            assert resp.status_code == 200
            assert resp.json()["first_name"] == "Jane"

           
            resp = await ac.delete(f"/contacts/{contact_id}", headers=headers)
            assert resp.status_code == 204

            
            resp = await ac.get(f"/contacts/{contact_id}", headers=headers)
            assert resp.status_code == 404
