from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from src import crud, schemas
from src.db import get_db
from src.deps import get_current_user
from src.models import User

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.post("/", response_model=schemas.ContactResponse, status_code=201)
def create_contact(
    contact: schemas.ContactCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new contact for the current user.

    Args:
        contact (schemas.ContactCreate): Contact creation data.
        db (Session): Database session.
        current_user (User): Authenticated user.

    Returns:
        schemas.ContactResponse: The created contact.
    """
    return crud.create_contact(db, contact, owner_id=current_user.id)


@router.get("/", response_model=List[schemas.ContactResponse])
def get_contacts(
    q: Optional[str] = Query(None, description="Search by name, surname or email"),
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a list of contacts for the current user, optionally filtered by search query.

    Args:
        q (Optional[str]): Search string for first name, last name, or email.
        skip (int): Number of records to skip.
        limit (int): Maximum number of records to return.
        db (Session): Database session.
        current_user (User): Authenticated user.

    Returns:
        List[schemas.ContactResponse]: List of matching contacts.
    """
    return crud.search_contacts(db, owner_id=current_user.id, q=q, skip=skip, limit=limit)


@router.get("/{contact_id}", response_model=schemas.ContactResponse)
def get_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a single contact by ID for the current user.

    Args:
        contact_id (int): ID of the contact.
        db (Session): Database session.
        current_user (User): Authenticated user.

    Raises:
        HTTPException: 404 if contact is not found.

    Returns:
        schemas.ContactResponse: The requested contact.
    """
    obj = crud.get_contact(db, contact_id, owner_id=current_user.id)
    if not obj:
        raise HTTPException(status_code=404, detail="Contact not found")
    return obj


@router.put("/{contact_id}", response_model=schemas.ContactResponse)
def update_contact(
    contact_id: int,
    contact: schemas.ContactUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update an existing contact for the current user.

    Args:
        contact_id (int): ID of the contact to update.
        contact (schemas.ContactUpdate): Data to update.
        db (Session): Database session.
        current_user (User): Authenticated user.

    Raises:
        HTTPException: 404 if contact is not found.

    Returns:
        schemas.ContactResponse: Updated contact.
    """
    obj = crud.update_contact(db, contact_id, contact, owner_id=current_user.id)
    if not obj:
        raise HTTPException(status_code=404, detail="Contact not found")
    return obj


@router.delete("/{contact_id}", status_code=204)
def delete_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a contact for the current user.

    Args:
        contact_id (int): ID of the contact to delete.
        db (Session): Database session.
        current_user (User): Authenticated user.

    Raises:
        HTTPException: 404 if contact is not found.

    Returns:
        None
    """
    ok = crud.delete_contact(db, contact_id, owner_id=current_user.id)
    if not ok:
        raise HTTPException(status_code=404, detail="Contact not found")
    return None


@router.get("/upcoming-birthdays", response_model=List[schemas.ContactResponse])
def get_birthdays(
    days: int = 7,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get contacts with birthdays in the next given number of days.

    Args:
        days (int): Number of days to look ahead for birthdays.
        db (Session): Database session.
        current_user (User): Authenticated user.

    Returns:
        List[schemas.ContactResponse]: Contacts with upcoming birthdays.
    """
    contacts = crud.get_upcoming_birthdays(db, days=days)
    return [c for c in contacts if c.owner_id == current_user.id]
