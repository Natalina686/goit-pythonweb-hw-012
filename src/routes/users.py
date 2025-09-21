from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from src.deps import get_current_user
from src.db import get_db
from src import crud, schemas
from cloudinary.uploader import upload as cloud_upload
from os import getenv
import time

router = APIRouter(prefix="/users", tags=["users"])


RATE = {}
LIMIT = 5  
WINDOW = 60

def check_rate(user_id: int) -> bool:
    """
    Check if the user has exceeded the request rate limit.

    Args:
        user_id (int): ID of the user.

    Returns:
        bool: True if request is allowed, False if rate limit exceeded.
    """
    now = time.time()
    last_reset, count = RATE.get(user_id, (now, 0))
    if now - last_reset > WINDOW:
        RATE[user_id] = (now, 1)
        return True
    else:
        if count >= LIMIT:
            return False
        RATE[user_id] = (last_reset, count + 1)
        return True


@router.get("/me", response_model=schemas.UserResponse)
def me(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Get information about the currently authenticated user.

    Applies rate limiting.

    Args:
        current_user (User): Authenticated user.
        db (Session): Database session.

    Raises:
        HTTPException: 429 if rate limit exceeded.

    Returns:
        schemas.UserResponse: User information.
    """
    if not check_rate(current_user.id):
        raise HTTPException(status_code=429, detail="Too many requests")
    return current_user


@router.post("/me/avatar", response_model=schemas.UserResponse)
def upload_avatar(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload a new avatar for the current user to Cloudinary.

    Args:
        file (UploadFile): Image file to upload.
        current_user (User): Authenticated user.
        db (Session): Database session.

    Returns:
        schemas.UserResponse: Updated user information with new avatar URL.
    """
    cloud_name = getenv("CLOUDINARY_CLOUD_NAME")
    api_key = getenv("CLOUDINARY_API_KEY")
    api_secret = getenv("CLOUDINARY_API_SECRET")
    
    import cloudinary
    cloudinary.config(cloud_name=cloud_name, api_key=api_key, api_secret=api_secret)
    
    res = cloud_upload(
        file.file, 
        folder="avatars", 
        public_id=f"user_{current_user.id}", 
        overwrite=True, 
        resource_type="image"
    )
    url = res.get("secure_url")
    updated = crud.update_user_avatar(db, current_user, url)
    return updated
