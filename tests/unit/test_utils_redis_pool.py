import pytest
from unittest.mock import AsyncMock
from src.auth.password_reset import generate_reset_token, verify_reset_token
from src.utils import redis_pool

@pytest.mark.anyio
async def test_fake_redis():
    redis = AsyncMock()
    redis.set.return_value = True
    redis.get.return_value = "value"
    redis.delete.return_value = True

    assert await redis.set("key", "value") is True
    assert await redis.get("key") == "value"
    assert await redis.delete("key") is True


def test_password_reset_token():
    email = "a@test.com"
    token = generate_reset_token(email)
    assert verify_reset_token(token) == email

def test_password_reset_token_roundtrip():
    
    email = "a@test.com"
    token = generate_reset_token(email)
    result = verify_reset_token(token)
    assert result == email


@pytest.mark.anyio
async def test_get_redis_connection_error(monkeypatch):
    """Якщо Redis недоступний — піднімається виняток"""
    async def fake_redis():
        raise ConnectionError("Redis down")

    monkeypatch.setattr(redis_pool, "get_redis", fake_redis)

    with pytest.raises(ConnectionError):
        await redis_pool.get_redis()



