import pytest
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models import Base, User, Contact


engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module")
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)

def test_create_user(db):
    user = User(email="user@test.com", hashed_password="hashed", full_name="Test User")
    db.add(user)
    db.commit()
    db.refresh(user)
    assert user.id is not None
    assert user.role == "user"
    assert user.is_active is True
    assert user.is_verified is False

def test_create_contact(db):
    
    user = User(email="owner@test.com", hashed_password="hashed", full_name="Owner")
    db.add(user)
    db.commit()
    db.refresh(user)

    contact = Contact(
        first_name="John",
        last_name="Doe",
        email="john@test.com",
        phone="123456",
        birthday=date(2000, 1, 1),
        owner_id=user.id
    )
    db.add(contact)
    db.commit()
    db.refresh(contact)

    assert contact.id is not None
    assert contact.owner_id == user.id
    assert contact.owner.email == "owner@test.com"

def test_user_contacts_relationship(db):
    user = db.query(User).filter(User.email == "owner@test.com").first()
    assert len(user.contacts) == 1
    assert user.contacts[0].first_name == "John"

