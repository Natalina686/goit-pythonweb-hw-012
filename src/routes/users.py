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

def check_rate(user_id):
    now = time.time()
    last_reset, count = RATE.get(user_id, (now, 0))
    if now - last_reset > WINDOW:
        RATE[user_id] = (now, 1)
        return True
    else:
        if count >= LIMIT:
            return False
        RATE[user_id] = (last_reset, count+1)
        return True

@router.get("/me", response_model=schemas.UserResponse)
def me(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    if not check_rate(current_user.id):
        raise HTTPException(status_code=429, detail="Too many requests")
    return current_user

@router.post("/me/avatar", response_model=schemas.UserResponse)
def upload_avatar(file: UploadFile = File(...), current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    
    cloud_name = getenv("CLOUDINARY_CLOUD_NAME")
    api_key = getenv("CLOUDINARY_API_KEY")
    api_secret = getenv("CLOUDINARY_API_SECRET")
    import cloudinary
    cloudinary.config(cloud_name=cloud_name, api_key=api_key, api_secret=api_secret)
    res = cloud_upload(file.file, folder="avatars", public_id=f"user_{current_user.id}", overwrite=True, resource_type="image")
    url = res.get("secure_url")
    updated = crud.update_user_avatar(db, current_user, url)
    return updated
