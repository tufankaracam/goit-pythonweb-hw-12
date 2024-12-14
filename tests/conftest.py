import asyncio

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from main import app
from src.database.models import Base, User
from src.database.db import get_db
from src.services.auth import create_access_token, Hash

# Database connection string for SQLite
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# Create a new async engine for the database
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Create a session maker for database transactions
TestingSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, expire_on_commit=False, bind=engine
)

# Mock data for a test user
test_user = {
    "id": 1,
    "username": "testuser",
    "email": "testuser@example.com",
    "password": "12345678",
    "role": "ADMIN",
    "confirmed": True,
}


@pytest.fixture(scope="module", autouse=True)
def init_models_wrap():
    """
    Initializes the database models for testing purposes.

    This fixture:
    - Drops all tables in the database.
    - Recreates all tables based on the `Base` metadata.
    - Inserts a test user into the database.

    The fixture is automatically executed once per test module.

    Returns:
        None
    """

    async def init_models():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        async with TestingSessionLocal() as session:
            hash_password = Hash().get_password_hash(test_user["password"])
            current_user = User(
                username=test_user["username"],
                email=test_user["email"],
                hashed_password=hash_password,
                confirmed=True,
                role="ADMIN",
                avatar="https://twitter.com/gravatar",
            )
            session.add(current_user)
            await session.commit()

    asyncio.run(init_models())


@pytest.fixture(scope="module")
def client():
    """
    Provides a `TestClient` instance for API testing.

    Overrides the `get_db` dependency to use an in-memory SQLite database
    during the tests.

    Yields:
        TestClient: A client instance to make requests to the FastAPI application.
    """

    async def override_get_db():
        """
        Overrides the database session with a test session.

        Yields:
            AsyncSession: A session instance for testing.
        """
        async with TestingSessionLocal() as session:
            try:
                yield session
            except Exception as err:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)


@pytest_asyncio.fixture()
async def get_token():
    """
    Creates a JWT access token for the test user.

    This token can be used to authenticate API requests during tests.

    Returns:
        str: A JWT token for the test user.
    """
    token = await create_access_token(data={"sub": test_user["username"]})
    return token
