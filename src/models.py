from sqlalchemy import Column, Integer, String, Date, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from .db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(150), unique=True, index=True, nullable=False)
    hashed_password = Column(String(200), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    full_name = Column(String(200), nullable=True)
    avatar_url = Column(String(500), nullable=True)

    contacts = relationship("Contact", back_populates="owner")

class Contact(Base):
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