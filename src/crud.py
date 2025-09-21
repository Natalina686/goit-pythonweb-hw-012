from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, extract, and_
from datetime import date, timedelta
from fastapi import HTTPException
from . import models, schemas
from .security import get_password_hash, verify_password


def create_contact(db: Session, contact_in: schemas.ContactCreate, owner_id) -> models.Contact:
    """
    Create a new contact for a specific user.

    Args:
        db (Session): SQLAlchemy database session.
        contact_in (ContactCreate): Pydantic schema with contact data.
        owner_id (int): ID of the user who owns the contact.

    Returns:
        Contact: Created contact model instance.
    """
    db_obj = models.Contact(**contact_in.dict(), owner_id=owner_id)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_contact(db: Session, contact_id: int, owner_id: int) -> Optional[models.Contact]:
    """
    Retrieve a contact by its ID and owner.

    Args:
        db (Session): SQLAlchemy session.
        contact_id (int): ID of the contact to retrieve.
        owner_id (int): ID of the contact owner.

    Returns:
        Optional[Contact]: Contact if found, else None.
    """
    obj = db.get(models.Contact, contact_id)
    if not obj or obj.owner_id != owner_id:
        return None
    return obj


def search_contacts(
    db: Session,
    owner_id: int,
    q: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[models.Contact]:
    """
    Search contacts for a user optionally by a query string.

    Args:
        db (Session): SQLAlchemy session.
        owner_id (int): ID of the contact owner.
        q (str, optional): Search query (first name, last name, email). Defaults to None.
        skip (int, optional): Number of records to skip. Defaults to 0.
        limit (int, optional): Maximum number of records to return. Defaults to 100.

    Returns:
        List[Contact]: List of contacts matching criteria.
    """
    query = db.query(models.Contact).filter(models.Contact.owner_id == owner_id)
    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(
                models.Contact.first_name.ilike(like),
                models.Contact.last_name.ilike(like),
                models.Contact.email.ilike(like),
            )
        )
    return query.offset(skip).limit(limit).all()


def update_contact(db: Session, contact_id: int, contact_in: schemas.ContactUpdate, owner_id: int) -> Optional[models.Contact]:
    """
    Update an existing contact.

    Args:
        db (Session): SQLAlchemy session.
        contact_id (int): ID of the contact to update.
        contact_in (ContactUpdate): Pydantic schema with updated fields.
        owner_id (int): ID of the contact owner.

    Returns:
        Optional[Contact]: Updated contact if successful, else None.
    """
    db_obj = db.get(models.Contact, contact_id)
    if not db_obj or db_obj.owner_id != owner_id:
        return None
    for key, value in contact_in.dict(exclude_unset=True).items():
        setattr(db_obj, key, value)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_contact(db: Session, contact_id: int, owner_id: int) -> bool:
    """
    Delete a contact by ID.

    Args:
        db (Session): SQLAlchemy session.
        contact_id (int): ID of the contact to delete.
        owner_id (int): ID of the contact owner.

    Returns:
        bool: True if deleted, False if not found or not owned by user.
    """
    db_obj = db.get(models.Contact, contact_id)
    if not db_obj or db_obj.owner_id != owner_id:
        return False
    db.delete(db_obj)
    db.commit()
    return True


def get_upcoming_birthdays(db: Session, days: int = 7) -> List[models.Contact]:
    """
    Retrieve contacts with birthdays in the upcoming days.

    Args:
        db (Session): SQLAlchemy session.
        days (int, optional): Number of days ahead to check. Defaults to 7.

    Returns:
        List[Contact]: Contacts with birthdays in the given period.
    """
    today = date.today()
    dates = [( (today + timedelta(days=i)).month, (today + timedelta(days=i)).day ) for i in range(days + 1)]
    
    conds = [and_(extract('month', models.Contact.birthday) == m, extract('day', models.Contact.birthday) == d)
             for m, d in dates]
    query = db.query(models.Contact).filter(or_(*conds))
    return query.all()


def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """
    Retrieve a user by email.

    Args:
        db (Session): SQLAlchemy session.
        email (str): User email.

    Returns:
        Optional[User]: User if found, else None.
    """
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[models.User]:
    """
    Retrieve a user by ID.

    Args:
        db (Session): SQLAlchemy session.
        user_id (int): User ID.

    Returns:
        Optional[User]: User if found, else None.
    """
    return db.query(models.User).filter(models.User.id == user_id).first()


def create_user(db: Session, user_in: schemas.UserCreate) -> models.User:
    """
    Create a new user.

    Args:
        db (Session): SQLAlchemy session.
        user_in (UserCreate): Pydantic schema with user registration data.

    Returns:
        User: Created user model instance.
    """
    existing_user = get_user_by_email(db, user_in.email)
    if existing_user:
        raise HTTPException(status_code=409, detail="Email already registered")
    user = models.User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> Optional[models.User]:
    """
    Authenticate a user with email and password.

    Args:
        db (Session): SQLAlchemy session.
        email (str): User email.
        password (str): Plain password.

    Returns:
        Optional[User]: Authenticated user if credentials are correct, else None.
    """
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def set_user_verified(db: Session, user: models.User):
    """
    Mark a user as verified.

    Args:
        db (Session): SQLAlchemy session.
        user (User): User model to verify.

    Returns:
        User: Verified user model.
    """
    user.is_verified = True
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user_avatar(db: Session, user: models.User, avatar_url: str):
    """
    Update the user's avatar URL.

    Args:
        db (Session): SQLAlchemy session.
        user (User): User model.
        avatar_url (str): New avatar URL.

    Returns:
        User: Updated user model.
    """
    user.avatar_url = avatar_url
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
