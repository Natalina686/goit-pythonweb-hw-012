from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional

class ContactBase(BaseModel):
    """
    Base schema for a contact.

    Attributes:
        first_name (str): Contact's first name.
        last_name (str): Contact's last name.
        email (EmailStr): Contact's email address.
        phone (str): Contact's phone number.
        birthday (date): Contact's date of birth.
        extra_data (Optional[str]): Additional information about the contact.
    """
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    birthday: date
    extra_data: Optional[str] = None

class ContactCreate(ContactBase):
    """
    Schema for creating a new contact.

    Inherits from ContactBase.
    """
    pass

class ContactUpdate(BaseModel):
    """
    Schema for updating an existing contact.

    Attributes:
        first_name (Optional[str]): Contact's first name.
        last_name (Optional[str]): Contact's last name.
        email (Optional[EmailStr]): Contact's email address.
        phone (Optional[str]): Contact's phone number.
        birthday (Optional[date]): Contact's date of birth.
        extra_data (Optional[str]): Additional information about the contact.
    """
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    birthday: Optional[date] = None
    extra_data: Optional[str] = None

class ContactResponse(ContactBase):
    """
    Schema for returning contact data in responses.

    Attributes:
        id (int): Contact ID.
    """
    id: int

    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    """
    Schema for creating a new user.

    Attributes:
        email (EmailStr): User's email address.
        password (str): User's password.
        full_name (Optional[str]): User's full name.
    """
    email: EmailStr
    password: str
    full_name: Optional[str]

class UserResponse(BaseModel):
    """
    Schema for returning user data in responses.

    Attributes:
        id (int): User ID.
        email (EmailStr): User's email address.
        full_name (Optional[str]): User's full name.
        is_verified (bool): Whether the user's email is verified.
        avatar_url (Optional[str]): URL to the user's avatar.
    """
    id: int
    email: EmailStr
    full_name: Optional[str]
    is_verified: bool
    avatar_url: Optional[str]

    class Config:
        from_attributes = True

class Token(BaseModel):
    """
    Schema for JWT access tokens.

    Attributes:
        access_token (str): JWT access token.
        token_type (str): Type of the token (default "bearer").
    """
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """
    Schema for JWT token payload data.

    Attributes:
        user_id (Optional[int]): ID of the user associated with the token.
    """
    user_id: Optional[int] = None
