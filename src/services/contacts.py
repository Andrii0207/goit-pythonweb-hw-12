"""
Contact Management Service
===========================

This module defines the ContactService class, which provides methods for managing contacts.

Classes
-------
- ContactService: Provides operations for creating, retrieving, updating, and deleting contacts.

Methods
-------
- create_contact: Creates a new contact.
- get_contacts: Retrieves a list of contacts with optional filtering.
- get_birthdays: Retrieves contacts with upcoming birthdays.
- get_contact: Retrieves a specific contact by ID.
- update_contact: Updates an existing contact.
- remove_contact: Deletes a contact.
"""

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from src.repository.contacts import ContactRepository
from src.schemas import ContactCreate, ContactUpdate

class ContactService:
    """
    Service class for managing user contacts.
    """
    def __init__(self, db: AsyncSession):
        """
        Initialize the ContactService with a database session.

        :param db: Async database session.
        """
        self.repository = ContactRepository(db)


    async def create_contact(self, body: ContactCreate, user: User):
        """
        Create a new contact for the given user.

        :param body: Contact data for creation.
        :param user: The user creating the contact.
        :return: The created contact.
        """
        return await self.repository.create_contact(body, user)


    async def get_contacts(self, skip: int, limit: int, user: User, query: Optional[str]=None):
        """
        Retrieve a list of contacts for the given user.

        :param skip: Number of records to skip.
        :param limit: Maximum number of records to return.
        :param user: The user whose contacts are being retrieved.
        :param query: Optional search query to filter contacts.
        :return: A list of contacts.
        """
        return await self.repository.get_contacts(skip, limit, user, query)


    async def get_birthdays(self, user: User):
        """
        Retrieve contacts with upcoming birthdays for the given user.

        :param user: The user whose contacts are being checked.
        :return: A list of contacts with upcoming birthdays.
        """
        return await self.repository.get_birthdays(user)


    async def get_contact(self, contact_id: int, user: User):
        """
        Retrieve a specific contact by ID.

        :param contact_id: The ID of the contact to retrieve.
        :param user: The user requesting the contact.
        :return: The requested contact.
        """
        return await self.repository.get_contact_by_id(contact_id, user)


    async def update_contact(self, contact_id: int, body: ContactUpdate, user: User):
        """
        Update an existing contact.

        :param contact_id: The ID of the contact to update.
        :param body: The updated contact data.
        :param user: The user making the update request.
        :return: The updated contact.
        """
        return await self.repository.update_contact(contact_id, body, user)


    async def remove_contact(self, contact_id: int, user: User):
        """
        Delete a contact.

        :param contact_id: The ID of the contact to delete.
        :param user: The user requesting deletion.
        :return: The deleted contact.
        """
        return await self.repository.remove_contact(contact_id, user)