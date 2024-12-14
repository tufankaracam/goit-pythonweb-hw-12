from pydantic import BaseModel, Field, EmailStr, PastDate, ConfigDict
from datetime import datetime
from typing import List, Optional
from src.database.models import UserRole


class ContactModel(BaseModel):
    """
    Represents the model for a contact with validation and constraints.

    Attributes:
        firstname (str): The first name of the contact (max length: 50).
        lastname (str): The last name of the contact (max length: 50).
        email (EmailStr): The email address of the contact.
        phone (str): The phone number of the contact (max length: 50).
        birthdate (datetime): The birthdate of the contact (must be a past date).
        additional (Optional[str]): Additional information about the contact.
    """

    firstname: str = Field(max_length=50)
    lastname: str = Field(max_length=50)
    email: str = EmailStr()
    phone: str = Field(max_length=50)
    birthdate: datetime = PastDate()
    additional: Optional[str] = None


class ContactResponse(ContactModel):
    """
    Represents the response model for a contact.

    Inherits all fields from `ContactModel` and adds:
        id (int): The unique identifier of the contact.
    """

    id: int


class User(BaseModel):
    """
    Represents the user model with basic attributes.

    Attributes:
        id (int): The unique identifier of the user.
        username (str): The username of the user.
        email (str): The email address of the user.
        avatar (str): The avatar URL of the user.
        role (UserRole): The role of the user (e.g., admin or user).
    """

    id: int
    username: str
    email: str
    avatar: str
    role: UserRole

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    """
    Represents the model for creating a new user.

    Attributes:
        username (str): The username for the new user.
        email (str): The email address for the new user.
        password (str): The password for the new user.
    """

    username: str
    email: str
    password: str


class Token(BaseModel):
    """
    Represents the authentication token model.

    Attributes:
        access_token (str): The access token for authentication.
        token_type (str): The type of the token (e.g., bearer).
    """

    access_token: str
    token_type: str


class RequestEmail(BaseModel):
    """
    Represents the model for requesting an email operation.

    Attributes:
        email (EmailStr): The email address for the request.
    """

    email: EmailStr
