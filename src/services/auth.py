from sqlalchemy.orm.session import make_transient
from datetime import datetime, timedelta, timezone
from typing import Optional
import redis.asyncio as redis
import json
from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from jose import JWTError, jwt

from src.database.db import get_db
from src.conf.config import settings
from src.services.users import UserService
from src.database.models import UserRole, User
from src.schemas import User as UserModel

# Redis configuration
r = redis.Redis(host=settings.REDIS_HOST, port=6379, password=settings.REDIS_PASSWORD)
UTC = timezone.utc


class Hash:
    """
    A utility class for password hashing and verification.

    Attributes:
        pwd_context (CryptContext): Context for password hashing and verification.
    """

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify that a plain password matches a hashed password.

        Args:
            plain_password (str): The plain password to verify.
            hashed_password (str): The hashed password to compare against.

        Returns:
            bool: True if the password matches, False otherwise.
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """
        Hash a plain password.

        Args:
            password (str): The password to hash.

        Returns:
            str: The hashed password.
        """
        return self.pwd_context.hash(password)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def create_access_token(data: dict, expires_delta: Optional[int] = None) -> str:
    """
    Create a new JWT access token.

    Args:
        data (dict): The data to encode in the token.
        expires_delta (Optional[int]): The token's expiration time in seconds. Defaults to the value in settings.

    Returns:
        str: The encoded JWT token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + timedelta(seconds=expires_delta)
    else:
        expire = datetime.now(UTC) + timedelta(seconds=settings.JWT_EXPIRATION_SECONDS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    """
    Retrieve the current authenticated user.

    This function authenticates a user based on a JWT token,
    checks if the user exists in Redis cache, and if not,
    retrieves the user from the database. The user's data
    is cached in Redis for future requests.

    Args:
        token (str): The JWT token extracted from the request's Authorization header.
        db (Session): The SQLAlchemy database session, injected via dependency.

    Returns:
        User: The authenticated user object.

    Raises:
        HTTPException: If the token is invalid or the user does not exist.
        Exception: If there is an error processing Redis cached data or saving to Redis.

    Examples:
        Typical usage example:
        ```python
        user = await get_current_user(token, db)
        print(user.username)
        ```
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Redis cache kontrolü
    cached_user = await r.get(str(username))
    if cached_user:
        try:
            user_data = json.loads(cached_user.decode("utf-8"))
            cached_user_obj = UserModel(**user_data)
            user_instance = User(**cached_user_obj.model_dump(exclude_unset=True))
            return user_instance
        except Exception as e:
            print(f"Error processing Redis cached user: {e}")

    result = await db.execute(select(User).filter(User.username == username))
    user_instance = result.scalars().first()

    if not user_instance:
        raise credentials_exception

    try:
        redis_data = json.dumps(
            user_instance.to_dict(),
            default=lambda x: x.isoformat() if isinstance(x, datetime) else str(x),
        )
        await r.set(str(username), redis_data)
        await r.expire(str(username), 3600)
    except Exception as e:
        print(f"Redis save error: {e}")

    return user_instance


async def get_current_admin_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    """
    Retrieve the current authenticated admin user from the token.

    Args:
        token (str): The OAuth2 token from the request.
        db (Session): The database session.

    Returns:
        User: The authenticated admin user.

    Raises:
        HTTPException: If the token is invalid or the user does not have admin privileges.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user_service = UserService(db)
    user = await user_service.get_user_by_username(username)
    if user is None:
        raise credentials_exception
    if user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Insufficient access rights")
    return user


def create_email_token(data: dict) -> str:
    """
    Create a new email verification token.

    Args:
        data (dict): The data to encode in the token.

    Returns:
        str: The encoded email token.
    """
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(days=7)
    to_encode.update({"iat": datetime.now(UTC), "exp": expire})
    token = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token


async def get_email_from_token(token: str) -> str:
    """
    Decode an email address from a token.

    Args:
        token (str): The token to decode.

    Returns:
        str: The email address encoded in the token.

    Raises:
        HTTPException: If the token is invalid.
    """
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        email = payload.get("sub")
        return email
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid email verification token",
        )
