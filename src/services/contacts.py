from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from src.repository.contacts import ContactRepository
from src.schemas import ContactModel
from src.database.models import Contact, User


class ContactService:
    """
    A service class for managing contact-related operations.

    Attributes:
        repository (ContactRepository): The repository for managing contact data.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize the ContactService with a database session.

        Args:
            db (AsyncSession): The database session.
        """
        self.repository = ContactRepository(db)

    async def create_contact(self, body: ContactModel, user: User) -> Optional[Contact]:
        """
        Create a new contact for a user.

        Args:
            body (ContactModel): The data for the new contact.
            user (User): The user to whom the contact belongs.

        Returns:
            Contact: The created contact.
        """
        return await self.repository.create_contact(body, user)

    async def get_contacts(
        self,
        user: User,
        skip: int = 0,
        limit: int = 100,
        name: Optional[str] = None,
        lastname: Optional[str] = None,
        email: Optional[str] = None,
    ) -> List[Contact]:
        """
        Retrieve a list of contacts for a user with optional filtering.

        Args:
            user (User): The user whose contacts are being retrieved.
            skip (int, optional): The number of contacts to skip. Defaults to 0.
            limit (int, optional): The maximum number of contacts to retrieve. Defaults to 100.
            name (str, optional): Filter by contact's first name. Defaults to None.
            lastname (str, optional): Filter by contact's last name. Defaults to None.
            email (str, optional): Filter by contact's email. Defaults to None.

        Returns:
            List[Contact]: A list of contacts.
        """
        return await self.repository.get_contacts(
            user, skip, limit, name, lastname, email
        )

    async def get_contact(self, contact_id: int, user: User) -> Optional[Contact]:
        """
        Retrieve a specific contact by its ID.

        Args:
            contact_id (int): The ID of the contact to retrieve.
            user (User): The user to whom the contact belongs.

        Returns:
            Contact or None: The contact if found, otherwise None.
        """
        return await self.repository.get_contact_by_id(contact_id, user)

    async def update_contact(
        self, contact_id: int, body: ContactModel, user: User
    ) -> Optional[Contact]:
        """
        Update an existing contact.

        Args:
            contact_id (int): The ID of the contact to update.
            body (ContactModel): The updated contact data.
            user (User): The user to whom the contact belongs.

        Returns:
            Contact or None: The updated contact if found, otherwise None.
        """
        return await self.repository.update_contact(contact_id, body, user)

    async def remove_contact(self, contact_id: int, user: User) -> Optional[Contact]:
        """
        Remove a contact by its ID.

        Args:
            contact_id (int): The ID of the contact to remove.
            user (User): The user to whom the contact belongs.

        Returns:
            Contact or None: The removed contact if found, otherwise None.
        """
        return await self.repository.remove_contact(contact_id, user)

    async def get_upcoming_birthdays(self, user: User) -> List[Contact]:
        """
        Retrieve a list of contacts with upcoming birthdays within the next week.

        Args:
            user (User): The user whose contacts are being checked.

        Returns:
            List[Contact]: A list of contacts with upcoming birthdays.
        """
        return await self.repository.get_upcoming_birthdays(user)
