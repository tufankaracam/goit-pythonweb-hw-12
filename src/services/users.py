from sqlalchemy.ext.asyncio import AsyncSession
from libgravatar import Gravatar

from src.repository.users import UserRepository
from src.schemas import UserCreate, User
from src.database.models import UserRole


class UserService:
    """
    Service layer for user-related operations.

    This class provides methods to interact with the user repository
    and perform various user-related tasks such as creating users,
    retrieving user details, and updating user information.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize the UserService with a database session.

        Args:
            db (AsyncSession): The database session.
        """
        self.repository = UserRepository(db)

    async def create_user(self, body: UserCreate):
        """
        Create a new user with an optional Gravatar avatar.

        If a Gravatar is available for the user's email, it is used as the avatar.

        Args:
            body (UserCreate): The user creation data.

        Returns:
            User: The created user.
        """
        avatar = None
        try:
            g = Gravatar(body.email)
            avatar = g.get_image()
        except Exception as e:
            print(e)

        return await self.repository.create_user(body, avatar)

    async def get_user_by_id(self, user_id: int):
        """
        Retrieve a user by their ID.

        Args:
            user_id (int): The ID of the user.

        Returns:
            User | None: The user object if found, otherwise None.
        """
        return await self.repository.get_user_by_id(user_id)

    async def get_user_by_username(self, username: str):
        """
        Retrieve a user by their username.

        Args:
            username (str): The username of the user.

        Returns:
            User | None: The user object if found, otherwise None.
        """
        return await self.repository.get_user_by_username(username)

    async def get_user_by_email(self, email: str):
        """
        Retrieve a user by their email address.

        Args:
            email (str): The email address of the user.

        Returns:
            User | None: The user object if found, otherwise None.
        """
        return await self.repository.get_user_by_email(email)

    async def confirmed_email(self, email: str):
        """
        Confirm a user's email address.

        Args:
            email (str): The email address to confirm.

        Returns:
            None
        """
        return await self.repository.confirmed_email(email)

    async def update_avatar_url(self, email: str, url: str):
        """
        Update the avatar URL for a user.

        Args:
            email (str): The email address of the user.
            url (str): The new avatar URL.

        Returns:
            User: The updated user object.
        """
        return await self.repository.update_avatar_url(email, url)

    async def is_only_user(self):
        """
        Check if the user is the only one in the database.

        Returns:
            bool: True if the user is the only one, otherwise False.
        """
        return await self.repository.is_only_user()

    async def update_user_role(self, user_id: int, new_role: UserRole) -> UserRole:
        """
        Update the role of a user.

        Args:
            user_id (int): The ID of the user.
            new_role (UserRole): The new role to assign.

        Returns:
            UserRole: The updated role of the user.
        """
        return await self.repository.update_user_role(user_id, new_role)

    async def get_user_password(self, user_id: int) -> str:
        """
        Retrieve the hashed password of a user.

        Args:
            user_id (int): The ID of the user.

        Returns:
            str: The hashed password of the user.
        """
        return await self.repository.get_user_password(user_id)

    async def update_user_password(
        self, user_id: int, new_hashed_password: str
    ) -> User:
        """
        Update the password of a user.

        Args:
            user_id (int): The ID of the user.
            new_hashed_password (str): The new hashed password.

        Returns:
            User: The updated user object.
        """
        return await self.repository.update_user_password(user_id, new_hashed_password)
