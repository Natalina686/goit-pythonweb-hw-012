import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.db import Base
from src import crud, models, schemas

# Тестова БД
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

@pytest.fixture
def db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_create_user(db):
    user_in = schemas.UserCreate(email="a@test.com", password="pass123", full_name="Test User")
    user = crud.create_user(db, user_in)
    assert user.id is not None
    assert user.email == "a@test.com"

def test_authenticate_user(db):
    user = crud.authenticate_user(db, "a@test.com", "pass123")
    assert user is not None
