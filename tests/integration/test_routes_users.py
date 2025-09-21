import uuid
import pytest
from httpx import AsyncClient
from asgi_lifespan import LifespanManager
from unittest.mock import AsyncMock, patch
from src.main import app
from src.schemas import UserResponse

@pytest.mark.anyio
async def test_get_me_and_upload_avatar():
    email = f"avatar_{uuid.uuid4()}@test.com"

    
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None
    mock_redis.set.return_value = True

    
    mock_cloud_upload = AsyncMock(return_value={"url": "http://fake-cloudinary/avatar.png"})

  
    with patch("src.dependencies.auth.get_redis", return_value=mock_redis), \
         patch("src.routes.users.cloud_upload", mock_cloud_upload), \
         patch("src.routes.users.get_current_user", new_callable=AsyncMock) as mock_get_user:

        async with LifespanManager(app):
            async with AsyncClient(app=app, base_url="http://test") as client:

                
                register_data = {"email": email, "password": "123456"}
                resp = await client.post("/auth/register", json=register_data)
                assert resp.status_code == 201
                user_id = resp.json()["id"]

                
                login_data = {"username": email, "password": "123456"}
                resp = await client.post("/auth/login", data=login_data)
                token = resp.json()["access_token"]
                headers = {"Authorization": f"Bearer {token}"}

                
                mock_get_user.return_value = UserResponse(
                    id=user_id,
                    email=email,
                    full_name="Test User",
                    avatar_url=None,
                    is_verified=False,
                    is_active=True,
                    role="user"
                )


            resp = await client.get("/auth/me", headers=headers)

            assert resp.status_code == 200
            me_data = resp.json()
            assert me_data["email"] == email
            assert me_data["is_verified"] is False
            assert me_data["is_active"] is True
            assert me_data["role"] == "user"

            
            files = {"file": ("avatar.png", b"fake image data", "image/png")}
            resp = await client.post(f"/users/{user_id}/avatar-default", headers=headers, files=files)
            assert resp.status_code == 200
            json_resp = resp.json()
            assert "avatar" in json_resp