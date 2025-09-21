import pytest
from httpx import AsyncClient
from src.main import app

@pytest.mark.asyncio
async def test_get_me_and_upload_avatar():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        
        await ac.post("/auth/register", json={"email":"u@test.com","password":"pass123"})
        login_resp = await ac.post("/auth/login", data={"username":"u@test.com","password":"pass123"})
        token = login_resp.json()["access_token"]

        headers = {"Authorization": f"Bearer {token}"}

        
        resp = await ac.get("/users/me", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["email"] == "u@test.com"

        
        import io
        files = {"file": ("avatar.png", io.BytesIO(b"fake image"), "image/png")}
        resp = await ac.post("/users/me/avatar", headers=headers, files=files)
        assert resp.status_code == 200
        assert "avatar_url" in resp.json()
