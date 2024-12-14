from enum import Enum
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Table,
    ForeignKey,
    func,
    Date,
    Enum as SqlEnum,
)
from sqlalchemy.sql.sqltypes import DateTime
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, relationship
from datetime import datetime


class Base(DeclarativeBase):
    """
    Base class for SQLAlchemy ORM models.
    """

    pass


class UserRole(str, Enum):
    """
    Enumeration for user roles.

    Attributes:
        USER (str): Standard user role.
        ADMIN (str): Administrator role.
    """

    USER = "user"
    ADMIN = "admin"


class Contact(Base):
    """
    ORM model representing a contact.

    Attributes:
        id (int): Primary key for the contact.
        firstname (str): First name of the contact.
        lastname (str): Last name of the contact.
        email (str): Email address of the contact.
        phone (str): Phone number of the contact.
        birthdate (datetime): Birthdate of the contact.
        additional (str): Additional information about the contact.
        user_id (int): Foreign key referencing the user's ID.
        user (User): Relationship to the associated user.
    """

    __tablename__ = "contacts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    firstname: Mapped[str] = mapped_column(String(50), nullable=False)
    lastname: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(50), nullable=False)
    phone: Mapped[str] = mapped_column(String(50), nullable=False)
    birthdate: Mapped[datetime] = mapped_column(Date, nullable=False)
    additional: Mapped[str] = mapped_column(String(255), nullable=True)
    user_id = Column(
        "user_id", ForeignKey("users.id", ondelete="CASCADE"), default=None
    )
    user = relationship("User", backref="contacts")


class User(Base):
    """
    ORM model representing a user.

    Attributes:
        id (int): Primary key for the user.
        username (str): Unique username of the user.
        email (str): Unique email address of the user.
        hashed_password (str): Hashed password for authentication.
        created_at (datetime): Timestamp when the user was created.
        avatar (str): URL of the user's avatar image.
        confirmed (bool): Whether the user's email is confirmed. Defaults to False.
        role (UserRole): Role of the user (e.g., 'user', 'admin').

    Methods:
        to_dict(): Converts the user object into a dictionary representation.
    """

    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    avatar = Column(String(255), nullable=True)
    confirmed = Column(Boolean, default=False)
    role = Column(SqlEnum(UserRole), default=UserRole.USER, nullable=False)

    def to_dict(self):
        """
        Converts the user object into a dictionary representation.

        Returns:
            dict: A dictionary containing the user's attributes and their values.
        """
        return {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }

    @classmethod
    def from_dict(cls, data):
        required_fields = ["id", "username", "email", "hashed_password", "role"]
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            raise ValueError(f"Missing fields in data: {missing_fields}")
        return cls(
            id=data.get("id"),
            username=data.get("username"),
            email=data.get("email"),
            hashed_password=data.get("hashed_password"),
            avatar=data.get("avatar"),
            confirmed=data.get("confirmed"),
            role=data.get("role"),
        )
