"""
Authentication and Token Management Module
=============================================

This module provides authentication utilities, including password hashing,
JWT token generation and validation, and retrieving the current user.

Classes
-------
- Hash: Handles password hashing and verification.

Functions
---------
- create_access_token: Generates a JWT access token.
- get_current_user: Retrieves the authenticated user from a token.
- create_email_token: Generates a JWT token for email verification.
- get_email_from_token: Extracts email from a verification token.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from src.database.db import get_db
from src.conf.config import settings
from src.database.models import User, UserRole
from src.services.users import UserService

UTC = timezone.utc

class Hash:
    """
    Class for handling password hashing and verification using bcrypt.
    """
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password, hashed_password):
        """
        Verify a plain password against a hashed password.

        :param plain_password: The plain text password to check.
        :param hashed_password: The stored hashed password.
        :return: True if passwords match, False otherwise.
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        """
        Hash a password using bcrypt.

        :param password: The password to hash.
        :return: Hashed password.
        """
        return self.pwd_context.hash(password)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
async def create_access_token(data: dict, expires_delta: Optional[int] = None):
    """
    Generate a new JWT access token.

    :param data: The data to encode into the token.
    :param expires_delta: Expiration time in seconds. If None, default expiration is used.
    :return: Encoded JWT token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + timedelta(seconds=expires_delta)
    else:
        expire = datetime.now(UTC) + timedelta(seconds=settings.JWT_EXPIRATION_SECONDS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


async def create_refresh_token(data: dict, expires_delta: Optional[int] = None):
    """
       Creates a new refresh token (JWT) for the user.

       Args:
           data (dict): The data (user information) to encode in the token.
           expires_delta (Optional[int], optional): The expiration time in seconds. Defaults to None.

       Returns:
           str: The generated JWT refresh token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + timedelta(seconds=expires_delta)
    else:
        expire = datetime.now(UTC) + timedelta(days=10)
    to_encode.update({"exp": expire, "token_type": "refresh"})

    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_REFRESH_SECRET, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


async def verify_refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    """
        Validates the given refresh token and returns the user if valid.

        Args:
            refresh_token (str): The refresh token.
            db (Session): The database session.

        Returns:
            User: The user associated with the refresh token or None if invalid.
    """
    try:
        payload = jwt.decode(
            refresh_token, settings.JWT_REFRESH_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        username: str = payload.get("sub")
        token_type: str = payload.get("token_type")

        if username is None or token_type != "refresh":
            return None

        user_service = UserService(db)
        user = await user_service.get_user_by_username(username)

        if refresh_token != user.refresh_token:
            return None

        return user
    except JWTError as err:
        return None


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    """
    Retrieve the current authenticated user from the provided token.

    :param token: JWT access token.
    :param db: Database session.
    :return: Authenticated user object.
    :raises HTTPException: If the token is invalid or user does not exist.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        username = payload["sub"]
        if username is None:
            raise credentials_exception
    except JWTError as e:
        raise credentials_exception
    user_service = UserService(db)
    user = await user_service.get_user_by_username(username)
    if user is None:
        raise credentials_exception
    return user


def create_email_token(data: dict):
    """
    Generate a JWT token for email verification.

    :param data: Data to encode in the token.
    :return: Encoded JWT token.
    """
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(days=7)
    to_encode.update({"iat": datetime.now(UTC), "exp": expire})
    token = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token


async def get_email_from_token(token: str):
    """
    Extract email from a JWT email verification token.

    :param token: JWT token.
    :return: Extracted email if valid.
    :raises HTTPException: If the token is invalid.
    """
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        email = payload["sub"]
        return email
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Неправильний токен для перевірки електронної пошти",
        )


def get_current_admin_user(current_user: User = Depends(get_current_user)):
    if current_user.role not in [UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Недостатньо прав доступу")
    return current_user