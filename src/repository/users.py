"""
User Repository
================

This module contains the `UserRepository` class, which provides database
operations for user-related actions using SQLAlchemy's AsyncSession.

Classes:
    UserRepository: Handles user-related database operations.

"""

from typing import Union

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from src.schemas import UserCreate


class UserRepository:
    """
    Repository for user-related database operations.

    Attributes:
        db (AsyncSession): The database session instance.
    """
    def __init__(self, session: AsyncSession):
        """
        Initializes the repository with a database session.

        Args:
            session (AsyncSession): The database session.
        """
        self.db = session


    async def get_user_by_id(self, user_id: int) -> Union[User, None]:
        """
        Retrieves a user by their unique ID.

        Args:
            user_id (int): The ID of the user.

        Returns:
            Union[User, None]: The User object if found, else None.
        """
        stmt = select(User).filter_by(id=user_id)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()


    async def get_user_by_username(self, username: str) -> Union[User, None]:
        """
        Retrieves a user by their username.

        Args:
            username (str): The username of the user.

        Returns:
            Union[User, None]: The User object if found, else None.
        """
        stmt = select(User).filter_by(username=username)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()


    async def get_user_by_email(self, email: str) -> Union[User, None]:
        """
        Retrieves a user by their email address.

        Args:
            email (str): The email address of the user.

        Returns:
            Union[User, None]: The User object if found, else None.
        """
        stmt = select(User).filter_by(email=email)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()


    async def create_user(self, body: UserCreate, avatar: str = None) -> User:
        """
        Creates a new user in the database.

        Args:
            body (UserCreate): The user creation schema.
            avatar (str, optional): The URL of the user's avatar. Defaults to None.

        Returns:
            User: The newly created User object.
        """
        user = User(
            **body.model_dump(exclude_unset=True, exclude={"password"}),
            hashed_password=body.password,
            avatar=avatar
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user


    async def confirmed_email(self, email: str) -> None:
        """
        Marks a user's email as confirmed.

        Args:
            email (str): The email address of the user.
        """
        user = await self.get_user_by_email(email)
        user.confirmed = True
        await self.db.commit()


    async def update_avatar_url(self, email: str, url: str) -> User:
        """
        Updates the avatar URL of a user.

        Args:
            email (str): The email address of the user.
            url (str): The new avatar URL.

        Returns:
            User: The updated User object.
        """
        user = await self.get_user_by_email(email)
        user.avatar = url
        await self.db.commit()
        await self.db.refresh(user)
        return user


    async def set_refresh_token(self, user_id: int, refresh_token: str) -> None:
        """
        Updates the refresh token for a user.

        Args:
            user_id (int): The ID of the user to update.
            refresh_token (str): The new refresh token.
        """
        user = await self.get_user_by_id(user_id)
        if user:
            user.refresh_token = refresh_token
            await self.db.commit()