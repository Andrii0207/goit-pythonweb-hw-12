from datetime import datetime, timedelta
from typing import List, Optional
from typing import Union

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact, User
from src.schemas import ContactUpdate, ContactCreate

class ContactRepository:
    def __init__(self, session: AsyncSession):
        self.db = session

    # async def get_contacts(self, skip: int, limit: int, query: Optional[str]=None) -> List[Contact]:
    #     stmt = select(Contact).offset(skip).limit(limit)
    #     contacts = await self.db.execute(stmt)
    #     return contacts.scalars().all()

    async def get_contacts(self, skip: int, limit: int, user: User, query: Optional[str] = None) -> List[Contact]:
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
        stmt = select(Contact).filter_by(id=contact_id, user=user)
        contact = await self.db.execute(stmt)
        return contact.scalar_one_or_none()

    async def create_contact(self, body: ContactCreate, user: User) -> Contact:
        contact = Contact(**body.model_dump(exclude_unset=True), user=user)
        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)
        return contact

    async def update_contact(self, contact_id: int, body: ContactUpdate, user: User) -> Union[Contact, None]:
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
        contact = await self.get_contact_by_id(contact_id, user)
        if contact:
            await self.db.delete(contact)
            await self.db.commit()
        return contact

    async def get_birthdays(self, user: User) -> List[Contact]:
        today = datetime.today()
        week = today + timedelta(days=7)

        stmt = select(Contact).filter_by(user=user).filter(
            Contact.birth_date >= today,
            Contact.birth_date <= week
        ).order_by(Contact.birth_date)

        result = await self.db.execute(stmt)
        return result.scalars().all()
