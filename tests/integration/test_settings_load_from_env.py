import os
import pytest
from src.settings import Settings

@pytest.fixture
def mock_env(monkeypatch):
   
    monkeypatch.setenv("POSTGRES_USER", "test_user")
    monkeypatch.setenv("POSTGRES_PASSWORD", "test_pass")
    monkeypatch.setenv("POSTGRES_DB", "test_db")
    monkeypatch.setenv("DATABASE_URL", "postgresql://test_user:test_pass@localhost/test_db")
    monkeypatch.setenv("SECRET_KEY", "supersecret")
    monkeypatch.setenv("ALGORITHM", "HS256")
    monkeypatch.setenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    monkeypatch.setenv("CLOUDINARY_CLOUD_NAME", "cloud_name")
    monkeypatch.setenv("CLOUDINARY_API_KEY", "cloud_key")
    monkeypatch.setenv("CLOUDINARY_API_SECRET", "cloud_secret")
    monkeypatch.setenv("FRONTEND_URL", "http://localhost:3000")

def test_settings_load(mock_env):
    config = Settings()

    
    assert config.POSTGRES_USER == "test_user"
    assert config.POSTGRES_PASSWORD == "test_pass"
    assert config.POSTGRES_DB == "test_db"
    assert config.DATABASE_URL.startswith("postgresql://")

    assert config.SECRET_KEY == "supersecret"
    assert config.ALGORITHM == "HS256"
    assert isinstance(config.ACCESS_TOKEN_EXPIRE_MINUTES, int)

    assert config.CLOUDINARY_CLOUD_NAME == "cloud_name"
    assert config.CLOUDINARY_API_KEY == "cloud_key"
    assert config.CLOUDINARY_API_SECRET == "cloud_secret"
    assert config.FRONTEND_URL == "http://localhost:3000"
