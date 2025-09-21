from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import timedelta
from os import getenv
from src import schemas, crud, models
from src.db import get_db
from src.security import create_access_token
from fastapi.security import OAuth2PasswordRequestForm
from src.settings import settings
from jose import jwt, JWTError

router = APIRouter(prefix="/auth", tags=["auth"])



@router.post("/register", response_model=schemas.UserResponse, status_code=201)
def register(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = crud.get_user_by_email(db, user_in.email)
    if existing:
        raise HTTPException(status_code=409, detail="User already exists")
    user = crud.create_user(db, user_in)
    
    token = create_access_token({"sub": str(user.id)}, expires_delta=timedelta(hours=24))
    verification_link = f"{getenv('FRONTEND_URL')}/verify?token={token}"
    return user

@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    access_token = create_access_token({"sub": str(user.id)})
    return {"access_token": access_token, "token_type":"bearer"}


@router.get("/verify")
def verify_email(token: str, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = int(payload.get("sub"))
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid token")
    user = db.get(models.User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    crud.set_user_verified(db, user)
    return {"detail":"Email verified"}