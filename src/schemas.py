"""
Schemas Module
==============

This module defines Pydantic schemas for contacts and users.

Schemas
-------
- ContactBase: Base schema for a contact.
- ContactCreate: Schema for creating a new contact.
- ContactUpdate: Schema for updating an existing contact.
- ContactResponse: Schema for returning contact data.
- User: Schema for user data.
- UserCreate: Schema for user registration.
- Token: Schema for authentication token.
- RequestEmail: Schema for email-based requests.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr, ConfigDict

from src.database.models import UserRole


class ContactBase(BaseModel):
    """
    Base schema for contact information.
    """
    first_name: str = Field(..., max_length=50)
    last_name: str = Field(..., max_length=50)
    email: EmailStr = Field(..., max_length=100)
    phone: str = Field(..., max_length=15)
    birth_date: datetime
    additional_data: Optional[str] = None

    class Config:
        orm_mode = True

class ContactCreate(ContactBase):
    """
    Schema for creating a new contact.
    """
    pass


class ContactUpdate(BaseModel):
    """
    Schema for updating an existing contact.
    """
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    email: Optional[EmailStr] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=15)
    birth_date: Optional[datetime] = None
    additional_data: Optional[str] = None


    class Config:
        orm_mode = True


class ContactResponse(ContactBase):
    """
    Schema for returning contact data.
    """
    id: int

    class Config:
        orm_mode = True


class User(BaseModel):
    """
    Schema for user information.
    """
    id: int
    username: str
    email: str
    avatar: str
    role: UserRole

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    """
    Schema for user registration.
    """
    username: str
    email: str
    password: str
    role: UserRole


class Token(BaseModel):
    """
    Schema for authentication token.
    """
    access_token: str
    token_type: str
    refresh_token: str


class RequestEmail(BaseModel):
    """
    Schema for email-based requests.
    """
    email: EmailStr
