from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User, UserRole
from src.schemas import UserCreate


class UserRepository:
    """
    Repository class for managing user-related database operations.

    Attributes:
        db (AsyncSession): The database session for performing queries.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize the UserRepository with a database session.

        Args:
            session (AsyncSession): The database session.
        """
        self.db = session

    async def get_user_by_id(self, user_id: int) -> User | None:
        """
        Retrieve a user by their ID.

        Args:
            user_id (int): The ID of the user to retrieve.

        Returns:
            User | None: The user if found, otherwise None.
        """
        stmt = select(User).filter_by(id=user_id)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> User | None:
        """
        Retrieve a user by their username.

        Args:
            username (str): The username of the user to retrieve.

        Returns:
            User | None: The user if found, otherwise None.
        """
        stmt = select(User).filter_by(username=username)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> User | None:
        """
        Retrieve a user by their email.

        Args:
            email (str): The email address of the user to retrieve.

        Returns:
            User | None: The user if found, otherwise None.
        """
        stmt = select(User).filter_by(email=email)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def create_user(self, body: UserCreate, avatar: str = None) -> User:
        """
        Create a new user.

        Args:
            body (UserCreate): The data for the new user.
            avatar (str, optional): The avatar URL for the user. Defaults to None.

        Returns:
            User: The created user.
        """
        user = User(
            **body.model_dump(exclude_unset=True, exclude={"password"}),
            hashed_password=body.password,
            avatar=avatar,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def confirmed_email(self, email: str) -> None:
        """
        Confirm a user's email address.

        Args:
            email (str): The email address to confirm.

        Raises:
            ValueError: If the user with the given email does not exist.
        """
        user = await self.get_user_by_email(email)
        if user is None:
            raise ValueError(f"User with email {email} does not exist.")
        user.confirmed = True
        await self.db.commit()

    async def update_avatar_url(self, email: str, url: str) -> User:
        """
        Update a user's avatar URL.

        Args:
            email (str): The email address of the user.
            url (str): The new avatar URL.

        Returns:
            User: The updated user.
        """
        user = await self.get_user_by_email(email)
        user.avatar = url
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def is_only_user(self) -> bool:
        """
        Check if there is only one user in the database.

        Returns:
            bool: True if there is only one user, otherwise False.
        """
        stmt = select(User).limit(2)
        result = await self.db.execute(stmt)
        return len(result.scalars().all()) == 1

    async def update_user_role(self, user_id: int, new_role: UserRole) -> UserRole:
        """
        Update a user's role.

        Args:
            user_id (int): The ID of the user to update.
            new_role (UserRole): The new role for the user.

        Returns:
            UserRole: The updated role of the user.

        Raises:
            ValueError: If the user with the given ID does not exist.
        """
        user = await self.get_user_by_id(user_id)
        if user is None:
            raise ValueError(f"User with id {user_id} does not exist.")
        user.role = new_role
        await self.db.commit()
        await self.db.refresh(user)
        return user.role

    async def get_user_password(self, user_id: int) -> str:
        """
        Retrieve a user's hashed password.

        Args:
            user_id (int): The ID of the user.

        Returns:
            str: The hashed password of the user.

        Raises:
            ValueError: If the user with the given ID does not exist.
        """
        user = await self.get_user_by_id(user_id)
        if user is None:
            raise ValueError(f"User with id {user_id} does not exist.")
        return user.hashed_password

    async def update_user_password(
        self, user_id: int, new_hashed_password: str
    ) -> User:
        """
        Update a user's hashed password.

        Args:
            user_id (int): The ID of the user.
            new_hashed_password (str): The new hashed password.

        Returns:
            User: The updated user.

        Raises:
            ValueError: If the user with the given ID does not exist.
        """
        user = await self.get_user_by_id(user_id)
        if user is None:
            raise ValueError(f"User with id {user_id} does not exist.")
        user.hashed_password = new_hashed_password
        await self.db.commit()
        await self.db.refresh(user)
        return user
