from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import timedelta
from os import getenv
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt, JWTError
from src import db
from src import schemas, crud, models
from src.db import get_db
from src.security import create_access_token
from src.settings import settings
from src.auth.password_reset import generate_reset_token, verify_reset_token
from src.utils.redis_pool import get_redis
from src.dependencies.auth import get_current_user
from src.dependencies.roles import admin_required

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=schemas.UserResponse, status_code=201)
def register(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.

    Args:
        user_in (UserCreate): Pydantic schema containing `email`, `password`, `full_name`.
        db (Session): SQLAlchemy database session.

    Returns:
        User: Created user instance.
    """
    existing = crud.get_user_by_email(db, user_in.email)
    if existing:
        raise HTTPException(status_code=409, detail="User already exists")
    user = crud.create_user(db, user_in)
    token = create_access_token({"sub": str(user.id)}, expires_delta=timedelta(hours=24))
    verification_link = f"{getenv('FRONTEND_URL')}/verify?token={token}"
    return user


@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Authenticate user and return access token.

    Args:
        form_data (OAuth2PasswordRequestForm): Form data with `username` and `password`.
        db (Session): SQLAlchemy database session.

    Returns:
        dict: Contains `access_token` and `token_type`.
    """
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    access_token = create_access_token({"sub": str(user.id)})
    return {"access_token": access_token, "token_type":"bearer"}


@router.get("/verify")
def verify_email(token: str, db: Session = Depends(get_db)):
    """
    Verify user's email via token.

    Args:
        token (str): JWT verification token.
        db (Session): SQLAlchemy database session.

    Returns:
        dict: Detail message of verification result.
    """
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


@router.post("/password-reset-request")
def password_reset_request(payload: dict, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Request a password reset link for a user.

    Args:
        payload (dict): Contains `email` key.
        background_tasks (BackgroundTasks): FastAPI background tasks for sending email.
        db (Session): SQLAlchemy database session.

    Returns:
        dict: Contains reset token and info message.
    """
    email = payload.get("email")
    user = crud.get_user_by_email(db, email)
    if not user:
        return {"status": "ok"}
    token = generate_reset_token(email)
    reset_link = f"{getenv('FRONTEND_URL')}/reset-password?token={token}"
    
    redis = get_redis()
    import asyncio
    asyncio.create_task(redis.set(f"pwdreset:{token}", email, ex=3600))
    
    return {"reset_token": token, "detail": "Check your email for reset link"}


@router.post("/password-reset")
def password_reset(payload: dict, db: Session = Depends(get_db)):
    """
    Reset user password using token.

    Args:
        payload (dict): Contains `token` and `password`.
        db (Session): SQLAlchemy database session.

    Returns:
        dict: Status message of password reset.
    """
    token = payload.get("token")
    new_password = payload.get("password")
    email = verify_reset_token(token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    
    redis = get_redis()
    import asyncio
    stored = asyncio.run(redis.get(f"pwdreset:{token}"))
    if not stored:
        raise HTTPException(status_code=400, detail="Token invalid or used")

    user = crud.get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    hashed = crud.get_password_hash(new_password)
    user.hashed_password = hashed
    db.add(user)
    db.commit()
    db.refresh(user)
    
    asyncio.run(redis.delete(f"pwdreset:{token}"))
    return {"status": "ok", "detail": "Password updated successfully"}


@router.get("/me", response_model=schemas.UserResponse)
def get_me(current_user: dict = Depends(get_current_user)):
    """
    Get the current authenticated user.

    Args:
        current_user (dict): Current user from dependency.

    Returns:
        dict: User info.
    """
    return current_user


@router.post("/users/{user_id}/avatar-default")
async def set_default_avatar(user_id: int, current_admin=Depends(admin_required)):
    """
    Set default avatar for a user (admin-only).

    Args:
        user_id (int): ID of the user to update.
        current_admin: Current admin user dependency.

    Returns:
        dict: Status message with detail.
    """
    user = db.get(models.User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    default_avatar_url = "https://res.cloudinary.com/.../default_avatar.png"
    user.avatar = default_avatar_url
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"status": "ok", "detail": f"Avatar for user {user_id} set to default"}
