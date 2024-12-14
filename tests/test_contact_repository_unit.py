import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact, User
from src.repository.contacts import ContactRepository
from src.schemas import ContactModel


@pytest.fixture
def mock_session():
    """
    Fixture to provide a mock of the AsyncSession.

    Returns:
        AsyncMock: Mock object for AsyncSession.
    """
    mock_session = AsyncMock(spec=AsyncSession)
    return mock_session


@pytest.fixture
def contact_repository(mock_session):
    """
    Fixture to provide a ContactRepository instance with a mocked session.

    Args:
        mock_session (AsyncMock): Mocked AsyncSession.

    Returns:
        ContactRepository: Repository instance.
    """
    return ContactRepository(mock_session)


@pytest.fixture
def user():
    """
    Fixture to provide a mocked User instance.

    Returns:
        User: Mocked user instance.
    """
    return User(id=1, username="testuser")


@pytest.mark.asyncio
async def test_get_contacts(contact_repository, mock_session, user):
    """
    Test retrieving a list of contacts for a user.

    Args:
        contact_repository (ContactRepository): The contact repository instance.
        mock_session (AsyncMock): Mocked session.
        user (User): Mocked user instance.

    Asserts:
        - The number of retrieved contacts.
        - The properties of the first contact in the list.
    """
    # Setup mock
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [
        Contact(
            id=1,
            firstname="test contact",
            lastname="contact",
            email="test.contact@example.com",
            phone="+1234567890",
            birthdate="2024-12-13T04:31:17.916Z",
            additional="Some additional information",
            user=user,
        )
    ]
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    contacts = await contact_repository.get_contacts(skip=0, limit=10, user=user)

    # Assertions
    assert len(contacts) == 1
    assert contacts[0].firstname == "test contact"


@pytest.mark.asyncio
async def test_get_contact_by_id(contact_repository, mock_session, user):
    """
    Test retrieving a contact by ID.

    Args:
        contact_repository (ContactRepository): The contact repository instance.
        mock_session (AsyncMock): Mocked session.
        user (User): Mocked user instance.

    Asserts:
        - Contact is not None.
        - Contact ID and properties are correct.
    """
    # Setup mock
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = Contact(
        id=1,
        firstname="test contact",
        lastname="contact",
        email="test.contact@example.com",
        phone="+1234567890",
        birthdate="2024-12-13T04:31:17.916Z",
        additional="Some additional information",
        user=user,
    )
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    contact = await contact_repository.get_contact_by_id(contact_id=1, user=user)

    # Assertions
    assert contact is not None
    assert contact.id == 1
    assert contact.firstname == "test contact"


@pytest.mark.asyncio
async def test_create_contact(contact_repository, mock_session, user):
    """
    Test creating a new contact.

    Args:
        contact_repository (ContactRepository): The contact repository instance.
        mock_session (AsyncMock): Mocked session.
        user (User): Mocked user instance.

    Asserts:
        - The created contact's properties.
        - That session methods (add, commit, refresh) are called.
    """
    # Setup
    contact_data = ContactModel(
        firstname="test",
        lastname="contact",
        email="test.contact@example.com",
        phone="+1234567890",
        birthdate="2024-12-13T04:31:17.916Z",
        additional="Some additional information",
    )

    # Call method
    result = await contact_repository.create_contact(body=contact_data, user=user)

    # Assertions
    assert isinstance(result, Contact)
    assert result.firstname == "test"
    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(result)


@pytest.mark.asyncio
async def test_update_contact(contact_repository, mock_session, user):
    """
    Test updating an existing contact.

    Args:
        contact_repository (ContactRepository): The contact repository instance.
        mock_session (AsyncMock): Mocked session.
        user (User): Mocked user instance.

    Asserts:
        - The updated contact's properties.
        - That session commit and refresh methods are called.
    """
    # Setup
    contact_data = ContactModel(
        firstname="updated test",
        lastname="contact",
        email="test.contact@example.com",
        phone="+1234567890",
        birthdate="2024-12-13T04:31:17.916Z",
        additional="Some additional information",
    )
    existing_contact = Contact(
        id=1,
        firstname="test",
        lastname="contact",
        email="test.contact@example.com",
        phone="+1234567890",
        birthdate="2024-12-13T04:31:17.916Z",
        additional="Some additional information",
        user=user,
    )
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_contact
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    result = await contact_repository.update_contact(
        contact_id=1, body=contact_data, user=user
    )

    # Assertions
    assert result is not None
    assert result.firstname == "updated test"
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(existing_contact)


@pytest.mark.asyncio
async def test_remove_contact(contact_repository, mock_session, user):
    """
    Test removing a contact by ID.

    Args:
        contact_repository (ContactRepository): The contact repository instance.
        mock_session (AsyncMock): Mocked session.
        user (User): Mocked user instance.

    Asserts:
        - The removed contact's properties.
        - That session delete and commit methods are called.
    """
    # Setup
    existing_contact = Contact(
        id=1,
        firstname="contact to delete",
        lastname="contact",
        email="test.contact@example.com",
        phone="+1234567890",
        birthdate="2024-12-13T04:31:17.916Z",
        additional="Some additional information",
        user=user,
    )
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_contact
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    result = await contact_repository.remove_contact(contact_id=1, user=user)

    # Assertions
    assert result is not None
    assert result.firstname == "contact to delete"
    mock_session.delete.assert_awaited_once_with(existing_contact)
    mock_session.commit.assert_awaited_once()
