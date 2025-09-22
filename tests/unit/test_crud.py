import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi import HTTPException
from datetime import date, timedelta

from src.db import Base
from src import crud, models, schemas
from src.security import get_password_hash


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

def test_create_user_conflict(db):
    
    user = models.User(email="b@test.com", hashed_password="hash")
    db.add(user)
    db.commit()
    
    user_in = schemas.UserCreate(email="b@test.com", password="pass123", full_name="Conflict User")
    with pytest.raises(HTTPException) as exc_info:
        crud.create_user(db, user_in)
    assert exc_info.value.status_code == 409

def test_authenticate_user(db):
    user_in = schemas.UserCreate(email="c@test.com", password="pass123", full_name="Auth User")
    crud.create_user(db, user_in)
    
    user = crud.authenticate_user(db, "c@test.com", "pass123")
    assert user is not None
    assert user.email == "c@test.com"

def test_authenticate_user_wrong_password(db):
    user_in = schemas.UserCreate(email="d@test.com", password="pass123", full_name="WrongPass User")
    crud.create_user(db, user_in)
    
    user = crud.authenticate_user(db, "d@test.com", "wrongpass")
    assert user is None

def test_authenticate_user_nonexistent_email(db):
    user = crud.authenticate_user(db, "nonexistent@test.com", "pass123")
    assert user is None

def test_set_user_verified(db):
    user_in = schemas.UserCreate(email="e@test.com", password="pass123", full_name="Verify User")
    user = crud.create_user(db, user_in)
    
    assert not user.is_verified
    user = crud.set_user_verified(db, user)
    assert user.is_verified

def test_update_user_avatar(db):
    user_in = schemas.UserCreate(email="f@test.com", password="pass123", full_name="Avatar User")
    user = crud.create_user(db, user_in)
    
    user = crud.update_user_avatar(db, user, avatar_url="http://avatar.url/img.png")
    assert user.avatar_url == "http://avatar.url/img.png"

def test_create_and_get_contact(db):
    
    user_in = schemas.UserCreate(email="g@test.com", password="pass123", full_name="Contact Owner")
    user = crud.create_user(db, user_in)
    
    contact_in = schemas.ContactCreate(
        first_name="John", last_name="Doe", email="john@test.com", phone="123456",
        birthday=date(2000, 1, 1)
    )
    contact = crud.create_contact(db, contact_in, owner_id=user.id)
    assert contact.id is not None
    assert contact.first_name == "John"
    
    fetched = crud.get_contact(db, contact.id, owner_id=user.id)
    assert fetched.id == contact.id

def test_update_and_delete_contact(db):
    user_in = schemas.UserCreate(email="h@test.com", password="pass123", full_name="Contact Owner2")
    user = crud.create_user(db, user_in)
    
    contact_in = schemas.ContactCreate(
        first_name="Jane", last_name="Doe", email="jane@test.com", phone="654321",
        birthday=date(1995, 5, 5)
    )
    contact = crud.create_contact(db, contact_in, owner_id=user.id)
    
    update_in = schemas.ContactUpdate(first_name="Janet")
    contact = crud.update_contact(db, contact.id, update_in, owner_id=user.id)
    assert contact.first_name == "Janet"
    
    result = crud.delete_contact(db, contact.id, owner_id=user.id)
    assert result is True
    
    assert crud.get_contact(db, contact.id, owner_id=user.id) is None

def test_search_contacts(db):
    user_in = schemas.UserCreate(email="i@test.com", password="pass123", full_name="Search Owner")
    user = crud.create_user(db, user_in)
    
    c1 = schemas.ContactCreate(first_name="Alice", last_name="Smith", email="alice@test.com", phone="1", birthday=date(1990,1,1))
    c2 = schemas.ContactCreate(first_name="Bob", last_name="Jones", email="bob@test.com", phone="2", birthday=date(1991,2,2))
    crud.create_contact(db, c1, owner_id=user.id)
    crud.create_contact(db, c2, owner_id=user.id)
    
    results = crud.search_contacts(db, owner_id=user.id, q="Alice")
    assert len(results) == 1
    assert results[0].first_name == "Alice"

def test_get_upcoming_birthdays(db):
    user_in = schemas.UserCreate(email="j@test.com", password="pass123", full_name="Birthday Owner")
    user = crud.create_user(db, user_in)
    
    upcoming_date = date.today() + timedelta(days=1)
    contact_in = schemas.ContactCreate(
        first_name="Bday", last_name="User", email="bday@test.com", phone="999",
        birthday=upcoming_date
    )
    crud.create_contact(db, contact_in, owner_id=user.id)
    
    results = crud.get_upcoming_birthdays(db, days=2)
    assert any(c.email == "bday@test.com" for c in results)
