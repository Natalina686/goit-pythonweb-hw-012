import pytest
from httpx import AsyncClient
from asgi_lifespan import LifespanManager
from src.main import app

@pytest.mark.asyncio
async def test_crud_contacts():
    async with LifespanManager(app):
        async with AsyncClient(app=app, base_url="http://test") as ac:

            
            await ac.post("/auth/register", json={"email":"c@test.com","password":"pass123"})
            login_resp = await ac.post("/auth/login", data={"username":"c@test.com","password":"pass123"})
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

            
            resp = await ac.put(f"/contacts/{contact_id}", json={"first_name":"Jane"}, headers=headers)
            assert resp.status_code == 200
            assert resp.json()["first_name"] == "Jane"

          
            resp = await ac.delete(f"/contacts/{contact_id}", headers=headers)
            assert resp.status_code == 204
