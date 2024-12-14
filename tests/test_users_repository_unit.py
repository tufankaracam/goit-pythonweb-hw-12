import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User, UserRole
from src.repository.users import UserRepository
from src.schemas import UserCreate


@pytest.fixture
def mock_session():
    """
    Pytest fixture for creating a mocked AsyncSession.

    Returns:
        AsyncMock: Mocked AsyncSession object.
    """
    mock_session = AsyncMock(spec=AsyncSession)
    return mock_session


@pytest.fixture
def user_repository(mock_session):
    """
    Pytest fixture for creating a UserRepository instance with a mocked session.

    Args:
        mock_session (AsyncMock): Mocked AsyncSession object.

    Returns:
        UserRepository: UserRepository instance with mocked session.
    """
    return UserRepository(mock_session)


@pytest.fixture
def user():
    """
    Pytest fixture for creating a mocked user instance.

    Returns:
        User: Mocked User object.
    """
    return User(
        id=1,
        username="testuser",
        email="testuser@example.com",
        avatar="test",
        confirmed=True,
        role=UserRole.USER,
    )


@pytest.mark.asyncio
async def test_get_user_by_id(user_repository, mock_session, user):
    """
    Test for retrieving a user by their ID.

    Args:
        user_repository (UserRepository): Repository for user operations.
        mock_session (AsyncMock): Mocked AsyncSession object.
        user (User): Mocked user instance.

    Asserts:
        - The retrieved user is not None.
        - The user ID matches the expected value.
        - The username matches the expected value.
    """
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = user
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await user_repository.get_user_by_id(user_id=1)

    assert result is not None
    assert result.id == 1
    assert result.username == "testuser"


@pytest.mark.asyncio
async def test_get_user_by_username(user_repository, mock_session, user):
    """
    Test for retrieving a user by their username.

    Args:
        user_repository (UserRepository): Repository for user operations.
        mock_session (AsyncMock): Mocked AsyncSession object.
        user (User): Mocked user instance.

    Asserts:
        - The retrieved user is not None.
        - The username matches the expected value.
    """
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = user
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await user_repository.get_user_by_username(username="testuser")

    assert result is not None
    assert result.username == "testuser"


@pytest.mark.asyncio
async def test_get_user_by_email(user_repository, mock_session, user):
    """
    Test for retrieving a user by their email address.

    Args:
        user_repository (UserRepository): Repository for user operations.
        mock_session (AsyncMock): Mocked AsyncSession object.
        user (User): Mocked user instance.

    Asserts:
        - The retrieved user is not None.
        - The email matches the expected value.
    """
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = user
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await user_repository.get_user_by_email(email="testuser@example.com")

    assert result is not None
    assert result.email == "testuser@example.com"


@pytest.mark.asyncio
async def test_confirmed_email(user_repository, mock_session, user):
    """
    Test for confirming a user's email address.

    Args:
        user_repository (UserRepository): Repository for user operations.
        mock_session (AsyncMock): Mocked AsyncSession object.
        user (User): Mocked user instance.

    Asserts:
        - The user's email confirmation status is True.
        - The commit method is called once.
    """
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = user
    mock_session.execute = AsyncMock(return_value=mock_result)

    await user_repository.confirmed_email(email="testuser@example.com")

    assert user.confirmed is True
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_avatar_url(user_repository, mock_session, user):
    """
    Test for updating a user's avatar URL.

    Args:
        user_repository (UserRepository): Repository for user operations.
        mock_session (AsyncMock): Mocked AsyncSession object.
        user (User): Mocked user instance.

    Asserts:
        - The updated avatar URL matches the expected value.
        - The commit method is called once.
        - The refresh method is called with the user instance.
    """
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = user
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await user_repository.update_avatar_url(
        email="testuser@example.com", url="http://example.com/avatar.jpg"
    )

    assert result.avatar == "http://example.com/avatar.jpg"
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(user)


@pytest.mark.asyncio
async def test_update_user_role(user_repository, mock_session, user):
    """
    Test for updating a user's role.

    Args:
        user_repository (UserRepository): Repository for user operations.
        mock_session (AsyncMock): Mocked AsyncSession object.
        user (User): Mocked user instance.

    Asserts:
        - The updated role matches the expected value.
        - The user's role is updated correctly.
        - The commit method is called once.
        - The refresh method is called with the user instance.
    """
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = user
    mock_session.execute = AsyncMock(return_value=mock_result)

    new_role = UserRole.ADMIN
    result = await user_repository.update_user_role(user_id=1, new_role=new_role)

    assert result == new_role
    assert user.role == new_role
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(user)


@pytest.mark.asyncio
async def test_get_user_password(user_repository, mock_session, user):
    """
    Test for retrieving a user's hashed password by their ID.

    Args:
        user_repository (UserRepository): Repository for user operations.
        mock_session (AsyncMock): Mocked AsyncSession object.
        user (User): Mocked user instance.

    Asserts:
        - The retrieved hashed password matches the expected value.
    """
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = User(
        id=1,
        username="testuser",
        email="testuser@example.com",
        avatar="test",
        confirmed=False,
        role=UserRole.USER,
    )
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await user_repository.get_user_password(user_id=1)

    assert result == user.hashed_password


@pytest.mark.asyncio
async def test_update_user_password(user_repository, mock_session, user):
    """
    Test for updating a user's hashed password.

    Args:
        user_repository (UserRepository): Repository for user operations.
        mock_session (AsyncMock): Mocked AsyncSession object.
        user (User): Mocked user instance.

    Asserts:
        - The updated hashed password matches the expected value.
        - The commit method is called once.
        - The refresh method is called with the updated user instance.
    """
    # Mock setup
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = user  # Mock user instance
    mock_session.execute = AsyncMock(return_value=mock_result)
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()

    # New hashed password
    new_password = "newhashedpassword123"

    # Call the method
    result = await user_repository.update_user_password(
        user_id=1, new_hashed_password=new_password
    )

    # Assertions
    assert result.hashed_password == new_password  # Check if the password is updated
    mock_session.commit.assert_awaited_once()  # Check if commit is awaited
    mock_session.refresh.assert_awaited_once_with(user)  # Check if refresh is called
