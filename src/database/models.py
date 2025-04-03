"""
Database Models
==================

This module defines the SQLAlchemy ORM models for the application.

Classes:
    - `Base`: Declarative base class for SQLAlchemy models.
    - `Contact`: Represents a contact in the system.
    - `User`: Represents a user in the system.

"""

from sqlalchemy import Column, Integer, String, Boolean, func, Table
from sqlalchemy.orm import relationship, DeclarativeBase, declarative_base
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import DateTime, Date


# class Base(DeclarativeBase):
#     pass
Base = declarative_base()


class Contact(Base):
    """
        Contact model representing a contact entry in the database.

        Attributes:
            id (int): Primary key.
            first_name (str): First name of the contact.
            last_name (str): Last name of the contact.
            email (str): Unique email of the contact.
            phone (str): Phone number of the contact.
            birth_date (Date): Birth date of the contact.
            additional_data (str, optional): Additional information about the contact.
            user_id (int, optional): Foreign key reference to the user who owns this contact.
            user (User): Relationship to the User model.
    """
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    birth_date = Column(Date)
    additional_data = Column(String, nullable=True)
    user_id = Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), default=None)
    user = relationship("User", backref="notes")


class User(Base):
    """
    User model representing a user in the system.

    Attributes:
        id (int): Primary key.
        username (str): Unique username.
        email (str): Unique email address.
        hashed_password (str): Hashed password for authentication.
        created_at (DateTime): Timestamp when the user was created.
        avatar (str, optional): URL to the user's avatar.
        confirmed (bool): Whether the user's email is confirmed.
    """
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=func.now())
    avatar = Column(String(255), nullable=True)
    confirmed = Column(Boolean, default=False)
