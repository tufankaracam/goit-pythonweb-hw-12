import contextlib

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)

from src.conf.config import settings


class DatabaseSessionManager:
    """
    Manages the database sessions for asynchronous interactions with SQLAlchemy.

    Attributes:
        _engine (AsyncEngine | None): The SQLAlchemy asynchronous engine instance.
        _session_maker (async_sessionmaker): The factory for creating new database sessions.
    """

    def __init__(self, url: str):
        """
        Initialize the database session manager with the provided database URL.

        Args:
            url (str): The database connection URL.
        """
        self._engine: AsyncEngine | None = create_async_engine(url)
        self._session_maker: async_sessionmaker = async_sessionmaker(
            autoflush=False, autocommit=False, bind=self._engine
        )

    @contextlib.asynccontextmanager
    async def session(self):
        """
        Asynchronous context manager for database sessions.

        Yields:
            AsyncSession: A new database session.

        Raises:
            Exception: If the session maker is not initialized.
            SQLAlchemyError: If a SQLAlchemy-related error occurs during the session.
        """
        if self._session_maker is None:
            raise Exception("Database session is not initialized")
        session = self._session_maker()
        try:
            yield session
        except SQLAlchemyError as e:
            await session.rollback()
            raise
        finally:
            await session.close()


sessionmanager = DatabaseSessionManager(settings.DB_URL)


async def get_db():
    """
    Dependency function for retrieving a database session.

    Yields:
        AsyncSession: A database session to be used in FastAPI route handlers.
    """
    async with sessionmanager.session() as session:
        yield session
