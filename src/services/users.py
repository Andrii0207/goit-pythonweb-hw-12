"""
User Service Module
====================

This module provides user management services, including user creation, retrieval, and avatar management.

Classes
-------
- UserService: Handles operations related to user accounts.

Methods
-------
- create_user: Creates a new user and generates a Gravatar avatar if available.
- get_user_by_id: Retrieves a user by their unique ID.
- get_user_by_username: Retrieves a user by their username.
- get_user_by_email: Retrieves a user by their email address.
- confirmed_email: Confirms a user's email address.
- update_avatar_url: Updates the avatar URL for a user.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from libgravatar import Gravatar

from src.repository.users import UserRepository
from src.schemas import UserCreate

class UserService:
    """
    Service class for managing user accounts.
    """
    def __init__(self, db: AsyncSession):
        """
        Initialize the UserService with a database session.

        :param db: Async database session.
        """
        self.repository = UserRepository(db)

    async def create_user(self, body: UserCreate):
        """
         Create a new user and assign a Gravatar avatar if available.

         :param body: User data for creation.
         :return: The created user object.
         """
        avatar = None
        try:
            g = Gravatar(body.email)
            avatar = g.get_image()
        except Exception as e:
            print(e)

        return await self.repository.create_user(body, avatar)

    async def get_user_by_id(self, user_id: int):
        """
        Retrieve a user by their unique ID.

        :param user_id: The ID of the user to retrieve.
        :return: The user object if found.
        """
        return await self.repository.get_user_by_id(user_id)

    async def get_user_by_username(self, username: str):
        """
        Retrieve a user by their username.

        :param username: The username of the user.
        :return: The user object if found.
        """
        return await self.repository.get_user_by_username(username)

    async def get_user_by_email(self, email: str):
        """
        Retrieve a user by their email address.

        :param email: The email of the user.
        :return: The user object if found.
        """
        return await self.repository.get_user_by_email(email)

    async def confirmed_email(self, email: str):
        """
        Confirm a user's email address.

        :param email: The email to confirm.
        :return: The updated user object.
        """
        return await self.repository.confirmed_email(email)

    async def update_avatar_url(self, email: str, url: str):
        """
        Update the avatar URL for a user.

        :param email: The email of the user.
        :param url: The new avatar URL.
        :return: The updated user object.
        """
        return await self.repository.update_avatar_url(email, url)

    async def set_refresh_token(self, user_id: int, refresh_token: str) -> None:
        await self.repository.set_refresh_token(user_id, refresh_token)