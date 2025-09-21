from sqlalchemy import Column, Integer, String, Date, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from .db import Base


class User(Base):
    """
    Represents a user in the system.

    Attributes:
        id (int): Primary key.
        email (str): Unique email address of the user.
        hashed_password (str): Hashed password.
        is_active (bool): Whether the user is active. Default True.
        is_verified (bool): Whether the user's email is verified. Default False.
        full_name (str): Full name of the user.
        avatar_url (str): URL of the user's avatar image.
        role (str): Role of the user, e.g., 'user' or 'admin'. Default 'user'.
        contacts (List[Contact]): List of contacts owned by the user.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(150), unique=True, index=True, nullable=False)
    hashed_password = Column(String(200), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    full_name = Column(String(200), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    role: str = Column(String, default="user")

    contacts = relationship("Contact", back_populates="owner")


class Contact(Base):
    """
    Represents a contact belonging to a user.

    Attributes:
        id (int): Primary key.
        first_name (str): First name of the contact.
        last_name (str): Last name of the contact.
        email (str): Email of the contact.
        phone (str): Phone number.
        birthday (date): Birthday of the contact.
        extra_data (str): Additional optional information.
        owner_id (int): Foreign key to the User who owns this contact.
        owner (User): Relationship to the owner user.
    """
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    phone = Column(String(50), unique=False, nullable=False)
    birthday = Column(Date, nullable=False)
    extra_data = Column(Text, nullable=True)

    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    owner = relationship("User", back_populates="contacts")
