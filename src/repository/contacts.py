from typing import List, Optional
from datetime import date, timedelta, datetime
from sqlalchemy import func, select, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models import Contact, User
from src.schemas import ContactModel


class ContactRepository:
    """
    Repository class for managing contact-related database operations.

    Attributes:
        db (AsyncSession): The database session for performing queries.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize the ContactRepository with a database session.

        Args:
            session (AsyncSession): The database session.
        """
        self.db = session

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
        Retrieve a list of contacts for the given user with optional filters.

        Args:
            user (User): The user whose contacts are being retrieved.
            skip (int): Number of contacts to skip. Defaults to 0.
            limit (int): Maximum number of contacts to retrieve. Defaults to 100.
            name (Optional[str]): Filter by contact's first name. Defaults to None.
            lastname (Optional[str]): Filter by contact's last name. Defaults to None.
            email (Optional[str]): Filter by contact's email. Defaults to None.

        Returns:
            List[Contact]: A list of contacts matching the filters.
        """
        query = select(Contact).filter_by(user=user).offset(skip).limit(limit)
        filters = []

        if name:
            filters.append(Contact.firstname.ilike(f"%{name}%"))
        if lastname:
            filters.append(Contact.lastname.ilike(f"%{lastname}%"))
        if email:
            filters.append(Contact.email.ilike(f"%{email}%"))

        if filters:
            query = query.where(or_(*filters))

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_contact_by_id(self, contact_id: int, user: User) -> Contact | None:
        """
        Retrieve a contact by its ID.

        Args:
            contact_id (int): The ID of the contact to retrieve.
            user (User): The user whose contact is being retrieved.

        Returns:
            Contact | None: The contact if found, otherwise None.
        """
        stmt = select(Contact).filter_by(id=contact_id, user=user)
        contact = await self.db.execute(stmt)
        return contact.scalar_one_or_none()

    async def create_contact(self, body: ContactModel, user: User) -> Contact:
        """
        Create a new contact for the given user.

        Args:
            body (ContactModel): The contact data to create.
            user (User): The user to associate the contact with.

        Returns:
            Contact: The created contact.
        """

        contact = Contact(**body.model_dump(exclude_unset=True))
        contact.user_id = user.id
        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)
        return contact

    async def update_contact(
        self, contact_id: int, body: ContactModel, user: User
    ) -> Contact | None:
        """
        Update an existing contact.

        Args:
            contact_id (int): The ID of the contact to update.
            body (ContactModel): The updated contact data.
            user (User): The user associated with the contact.

        Returns:
            Contact | None: The updated contact if found, otherwise None.
        """
        contact = await self.get_contact_by_id(contact_id, user)
        if contact:
            contact.firstname = body.firstname
            contact.lastname = body.lastname
            contact.email = body.email
            contact.phone = body.phone
            contact.birthdate = body.birthdate
            contact.additional = body.additional

            await self.db.commit()
            await self.db.refresh(contact)
        return contact

    async def remove_contact(self, contact_id: int, user: User) -> Contact | None:
        """
        Remove a contact by its ID.

        Args:
            contact_id (int): The ID of the contact to remove.
            user (User): The user associated with the contact.

        Returns:
            Contact | None: The removed contact if found, otherwise None.
        """
        contact = await self.get_contact_by_id(contact_id, user)
        if contact:
            await self.db.delete(contact)
            await self.db.commit()
        return contact

    async def get_upcoming_birthdays(self, user: User) -> List[Contact]:
        """
        Retrieve contacts with upcoming birthdays within the next 7 days.

        Args:
            user (User): The user whose contacts are being retrieved.

        Returns:
            List[Contact]: A list of contacts with upcoming birthdays.
        """
        today = datetime.utcnow()
        next_week = today + timedelta(days=7)

        stmt = select(Contact).filter(
            and_(
                func.date_part("month", Contact.birthdate) == today.month,
                func.date_part("day", Contact.birthdate) >= today.day,
                func.date_part("month", Contact.birthdate) == next_week.month,
                func.date_part("day", Contact.birthdate) <= next_week.day,
                Contact.user_id == user.id,
            )
        )

        results = await self.db.execute(stmt)
        return results.scalars().all()
