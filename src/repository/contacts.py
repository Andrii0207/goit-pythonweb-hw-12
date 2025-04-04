"""
Contact Repository
==================

This module provides database operations for managing contacts.

Classes:
    - `ContactRepository`: Handles CRUD operations for contacts.

"""

from datetime import datetime, timedelta
from typing import List, Optional
from typing import Union

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact, User
from src.schemas import ContactUpdate, ContactCreate

class ContactRepository:
    """
    Repository class for handling contact-related database operations.

    Attributes:
        db (AsyncSession): The database session.
    """
    def __init__(self, session: AsyncSession):
        """
        Initializes the repository with a database session.

        Args:
            session (AsyncSession): The database session.
        """
        self.db = session

    async def get_contacts(self, skip: int, limit: int, user: User, query: Optional[str] = None) -> List[Contact]:
        """
        Retrieves a list of contacts for a user with optional search query.

        Args:
            skip (int): Number of records to skip.
            limit (int): Maximum number of records to retrieve.
            user (User): The owner of the contacts.
            query (Optional[str]): Search term to filter contacts by name or email.

        Returns:
            List[Contact]: List of contact objects.
        """
        stmt = select(Contact).filter_by(user=user).offset(skip).limit(limit)
        if query:
            stmt = stmt.filter(
                or_(
                    Contact.first_name.ilike(f"%{query}%"),
                    Contact.last_name.ilike(f"%{query}%"),
                    Contact.email.ilike(f"%{query}%")
                )
            )
        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()

    async def get_contact_by_id(self, contact_id: int, user: User) -> Union[Contact, None]:
        """
        Retrieves a contact by its ID.

        Args:
            contact_id (int): The ID of the contact.
            user (User): The owner of the contact.

        Returns:
            Union[Contact, None]: The contact object if found, otherwise None.
        """
        stmt = select(Contact).filter_by(id=contact_id, user=user)
        contact = await self.db.execute(stmt)
        return contact.scalar_one_or_none()

    async def create_contact(self, body: ContactCreate, user: User) -> Contact:
        """
        Creates a new contact for the user.

        Args:
            body (ContactCreate): The contact details.
            user (User): The owner of the contact.

        Returns:
            Contact: The created contact object.
        """
        contact = Contact(**body.model_dump(exclude_unset=True), user=user)
        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)
        return contact

    async def update_contact(self, contact_id: int, body: ContactUpdate, user: User) -> Union[Contact, None]:
        """
        Updates an existing contact's details.

        Args:
            contact_id (int): The ID of the contact.
            body (ContactUpdate): The new contact details.
            user (User): The owner of the contact.

        Returns:
            Union[Contact, None]: The updated contact object if found, otherwise None.
        """
        contact = await self.get_contact_by_id(contact_id, user)
        if contact:
            contact.first_name = body.first_name
            contact.last_name = body.last_name
            contact.email = body.email
            contact.phone = body.phone
            contact.birth_date = body.birth_date
            contact.additional_data = body.additional_data
            await self.db.commit()
            await self.db.refresh(contact)
        return contact

    async def remove_contact(self, contact_id: int, user: User) -> Union[Contact, None]:
        """
        Deletes a contact by its ID.

        Args:
            contact_id (int): The ID of the contact to delete.
            user (User): The owner of the contact.

        Returns:
            Union[Contact, None]: The deleted contact object if found, otherwise None.
        """
        contact = await self.get_contact_by_id(contact_id, user)
        if contact:
            await self.db.delete(contact)
            await self.db.commit()
        return contact

    async def get_birthdays(self, user: User) -> List[Contact]:
        """
        Retrieves contacts with upcoming birthdays in the next 7 days.

        Args:
            user (User): The owner of the contacts.

        Returns:
            List[Contact]: List of contacts with upcoming birthdays.
        """
        today = datetime.today()
        week = today + timedelta(days=7)

        stmt = select(Contact).filter_by(user=user).filter(
            Contact.birth_date >= today,
            Contact.birth_date <= week
        ).order_by(Contact.birth_date)

        result = await self.db.execute(stmt)
        return result.scalars().all()
