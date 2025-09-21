from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional

class ContactBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    birthday: date
    extra_data: Optional[str] = None

class ContactCreate(ContactBase):
    pass

class ContactUpdate(BaseModel):
   
   first_name: Optional[str] = None
   last_name: Optional[str] = None
   email: Optional[EmailStr] = None
   phone: Optional[str] = None
   birthday: Optional[date] = None
   extra_data: Optional[str] = None

class ContactResponse(ContactBase):
    id: int

    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str]

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str]
    is_verified: bool
    avatar_url: Optional[str]

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: Optional[int] = None