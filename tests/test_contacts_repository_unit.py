import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from src.database.models import Contact, User
from src.repository.contacts import ContactRepository
from src.schemas import ContactCreate, ContactUpdate


@pytest.fixture
def mock_session():
    return AsyncMock(spec=AsyncSession)

@pytest.fixture
def contact_repository(mock_session):
    return ContactRepository(mock_session)

@pytest.fixture
def user():
    return User(id=1, username="testuser")


@pytest.mark.asyncio
async def test_get_contacts(contact_repository, mock_session, user):
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [Contact(id=1, first_name="Ivan", last_name="Ivanov", user=user)]
    mock_session.execute = AsyncMock(return_value=mock_result)
    contacts = await contact_repository.get_contacts(skip=0, limit=10, user=user)
    assert len(contacts) == 1
    assert contacts[0].first_name == "Ivan"
    assert contacts[0].last_name == "Ivanov"


@pytest.mark.asyncio
async def test_get_contact_by_id(contact_repository, mock_session, user):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = Contact(id=1, first_name="Ivan", last_name="Ivanov", user=user)
    mock_session.execute = AsyncMock(return_value=mock_result)
    contact = await contact_repository.get_contact_by_id(contact_id=1, user=user)

    assert contact is not None
    assert contact.first_name == "Ivan"
    assert contact.last_name == "Ivanov"


@pytest.mark.asyncio
async def test_create_contact(contact_repository, mock_session, user):
    contact_data = ContactCreate(
        first_name="Ivan",
        last_name="Ivanov",
        email="Ivan@example.com",
        phone="+0123456789",
        birth_date="2020-01-01"
    )

    result = await contact_repository.create_contact(body=contact_data, user=user)

    assert isinstance(result, Contact)
    assert result.first_name == "Ivan"
    assert result.last_name == "Ivanov"
    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(result)


@pytest.mark.asyncio
async def test_update_contact(contact_repository, mock_session, user):

    contact_data = ContactUpdate(first_name="Updated Ivan", last_name="Updated Ivanov")
    existing_contact = Contact(id=1, first_name="Ivan", last_name="Ivanov", user=user)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_contact
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await contact_repository.update_contact(contact_id=1, body=contact_data, user=user)

    assert result is not None
    assert result.first_name == "Updated Ivan"
    assert result.last_name == "Updated Ivanov"
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(existing_contact)


@pytest.mark.asyncio
async def test_remove_contact(contact_repository, mock_session, user):

    existing_contact = Contact(id=1, first_name="Ivan", last_name="Ivanov", user=user)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_contact
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await contact_repository.remove_contact(contact_id=1, user=user)

    assert result is not None
    assert result.first_name == "Ivan"
    assert result.last_name == "Ivanov"
    mock_session.delete.assert_awaited_once_with(existing_contact)
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_birthdays(contact_repository, mock_session, user):

    today = datetime.today()
    seven_days_later = today + timedelta(days=7)
    contact_data = Contact(id=1, first_name="Ivan", last_name="Ivanov", user=user, birth_date=today + timedelta(days=5))
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [contact_data]
    mock_session.execute = AsyncMock(return_value=mock_result)

    contacts = await contact_repository.get_birthdays(user=user)

    assert len(contacts) == 1
    assert contacts[0].first_name == "Ivan"
    assert contacts[0].birth_date <= seven_days_later
