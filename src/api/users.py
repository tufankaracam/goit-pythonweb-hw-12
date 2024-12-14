from fastapi import APIRouter, Depends, Request, UploadFile, File, HTTPException, status
from fastapi.responses import JSONResponse

from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.database.models import UserRole
from src.schemas import User
from src.conf.config import settings
from src.services.auth import get_current_user, get_current_admin_user
from src.services.users import UserService
from src.services.upload_file import UploadFileService
from src.services.auth import Hash

router = APIRouter(prefix="/users", tags=["users"])
limiter = Limiter(key_func=get_remote_address)


@router.get(
    "/me", response_model=User, description="No more than 10 requests per minute"
)
@limiter.limit("10/minute")
async def me(request: Request, user: User = Depends(get_current_user)):
    """
    Retrieve the profile information of the currently authenticated user.

    Args:
        request (Request): The HTTP request object.
        user (User): The currently authenticated user.

    Returns:
        User: The user's profile information.
    """
    return user


@router.patch("/avatar", response_model=User)
async def update_avatar_user(
    file: UploadFile = File(),
    user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update the avatar of an authenticated admin user.

    Args:
        file (UploadFile): The new avatar file to upload.
        user (User): The currently authenticated admin user.
        db (AsyncSession): The database session dependency.

    Returns:
        User: The user object with the updated avatar URL.
    """
    avatar_url = UploadFileService(
        settings.CLD_NAME, settings.CLD_API_KEY, settings.CLD_API_SECRET
    ).upload_file(file, user.username)

    user_service = UserService(db)
    user = await user_service.update_avatar_url(user.email, avatar_url)

    return user


@router.patch("/update-role", response_model=UserRole)
async def update_avatar_user(
    user_id: int,
    new_role: UserRole,
    user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update the role of a user. Only admin users can perform this action.

    Args:
        user_id (int): The ID of the user whose role will be updated.
        new_role (UserRole): The new role to assign to the user.
        user (User): The currently authenticated admin user.
        db (AsyncSession): The database session dependency.

    Returns:
        UserRole: The updated role of the user.

    Raises:
        HTTPException: If the admin attempts to change their own role or if another error occurs.
    """
    if user_id == user.id:
        raise HTTPException(status_code=406, detail="Admin can not change self role")
    user_service = UserService(db)
    role = await user_service.update_user_role(user_id, new_role)
    return role


@router.patch("/update-password", status_code=status.HTTP_200_OK)
async def update_password(
    old_password: str,
    new_password1: str,
    new_password2: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update the password of the currently authenticated user.

    Args:
        old_password (str): The user's current password.
        new_password1 (str): The new password to set.
        new_password2 (str): The new password confirmation.
        user (User): The currently authenticated user.
        db (AsyncSession): The database session dependency.

    Returns:
        JSONResponse: A response indicating the password has been updated.

    Raises:
        HTTPException: If the current password is incorrect or if the new passwords do not match.
    """
    user_service = UserService(db)

    user_data = await user_service.get_user_by_id(user.id)
    if not user_data or not Hash().verify_password(
        old_password, user_data.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неправильний пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not new_password1 == new_password2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New Passwords are not matching",
            headers={"WWW-Authenticate": "Bearer"},
        )
    new_hashed_password = Hash().get_password_hash(new_password1)
    user_data = await user_service.update_user_password(
        user_data.id, new_hashed_password
    )
    return JSONResponse(content={"detail": "Password updated"})
