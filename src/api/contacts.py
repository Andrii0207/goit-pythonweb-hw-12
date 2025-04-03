"""
Contacts API
============

This module provides endpoints for managing user contacts, including:

- Retrieving a list of contacts.
- Fetching contacts with upcoming birthdays.
- Retrieving a single contact by ID.
- Creating a new contact.
- Updating an existing contact.
- Deleting a contact.

Endpoints:
    - `/contacts/` (GET): Retrieve a list of contacts.
    - `/contacts/birthdays` (GET): Get contacts with upcoming birthdays.
    - `/contacts/{contact_id}` (GET): Retrieve a specific contact by ID.
    - `/contacts/` (POST): Create a new contact.
    - `/contacts/{contact_id}` (PUT): Update an existing contact.
    - `/contacts/{contact_id}` (DELETE): Remove a contact.

"""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.database.models import User
from src.schemas import ContactResponse, ContactCreate, ContactUpdate
from src.services.auth import get_current_user
from src.services.contacts import ContactService

router = APIRouter(prefix="/contacts", tags=["contacts"])

@router.get("/", response_model=List[ContactResponse])
async def read_contacts(
        skip: int = 0,
        limit: int = 100,
        query: Optional[str]=None,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user)):
    """
        Retrieve a list of contacts.

        :param skip: Number of records to skip.
        :type skip: int
        :param limit: Maximum number of contacts to return.
        :type limit: int
        :param query: Optional search query.
        :type query: Optional[str]
        :param db: Database session.
        :type db: AsyncSession
        :param user: Authenticated user.
        :type user: User
        :return: List of contacts.
        :rtype: List[ContactResponse]
    """
    contact_service = ContactService(db)
    contacts = await contact_service.get_contacts(skip, limit, user, query)
    return contacts

@router.get("/birthdays", response_model=List[ContactResponse])
async def get_birthdays(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    """
       Retrieve contacts with upcoming birthdays.

       :param db: Database session.
       :type db: AsyncSession
       :param user: Authenticated user.
       :type user: User
       :return: List of contacts with upcoming birthdays.
       :rtype: List[ContactResponse]
    """
    contact_service = ContactService(db)
    contacts = await contact_service.get_birthdays(user)
    return contacts

@router.get("/{contact_id}", response_model=ContactResponse)
async def read_contact(
        contact_id: int,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user)):
    """
       Retrieve a contact by ID.

       :param contact_id: ID of the contact.
       :type contact_id: int
       :param db: Database session.
       :type db: AsyncSession
       :param user: Authenticated user.
       :type user: User
       :return: Contact details.
       :rtype: ContactResponse
       """
    contact_service = ContactService(db)
    contact = await contact_service.get_contact(contact_id, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact

@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
        body: ContactCreate,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user)):
    """
      Create a new contact.

      :param body: Contact creation details.
      :type body: ContactCreate
      :param db: Database session.
      :type db: AsyncSession
      :param user: Authenticated user.
      :type user: User
      :return: Newly created contact.
      :rtype: ContactResponse
    """
    contact_service = ContactService(db)
    return await contact_service.create_contact(body, user)

@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
        body: ContactUpdate,
        contact_id: int, db:
        AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user)):
    """
      Update an existing contact.

      :param body: Contact update details.
      :type body: ContactUpdate
      :param contact_id: ID of the contact to update.
      :type contact_id: int
      :param db: Database session.
      :type db: AsyncSession
      :param user: Authenticated user.
      :type user: User
      :return: Updated contact.
      :rtype: ContactResponse
    """
    contact_service = ContactService(db)
    contact = await contact_service.update_contact(contact_id, body, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact

@router.delete("/{contact_id}", response_model=ContactResponse)
async def remove_contact(
        contact_id: int,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user)):
    """
       Remove a contact.

       :param contact_id: ID of the contact to remove.
       :type contact_id: int
       :param db: Database session.
       :type db: AsyncSession
       :param user: Authenticated user.
       :type user: User
       :return: Deleted contact details.
       :rtype: ContactResponse
    """
    contact_service = ContactService(db)
    contact = await contact_service.remove_contact(contact_id, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact