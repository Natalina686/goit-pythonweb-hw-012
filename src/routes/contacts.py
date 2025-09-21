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
    return crud.create_contact(db, contact, owner_id=current_user.id)


@router.get("/", response_model=List[schemas.ContactResponse])
def get_contacts(
    q: Optional[str] = Query(None, description="Search by name, surname or email"),
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return crud.search_contacts(db, owner_id=current_user.id, q=q, skip=skip, limit=limit)


@router.get("/{contact_id}", response_model=schemas.ContactResponse)
def get_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
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
    contacts = crud.get_upcoming_birthdays(db, days=days)
    return [c for c in contacts if c.owner_id == current_user.id]
