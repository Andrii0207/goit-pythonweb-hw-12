"""
Users API
=========

This module provides endpoints for user-related operations, including:

- Retrieving the authenticated user's information.
- Updating the user's avatar.

Endpoints:
    - `/users/me` (GET): Retrieve the authenticated user's details.
    - `/users/avatar` (PATCH): Update the user's avatar.

"""

from fastapi import APIRouter, Depends, Request, UploadFile, File
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession

from src.conf.config import settings
from src.database.db import get_db
from src.schemas import User
from src.services.auth import get_current_user
from slowapi import Limiter

from src.services.upload_file import UploadFileService
from src.services.users import UserService

router = APIRouter(prefix="/users", tags=["users"])
limiter = Limiter(key_func=get_remote_address)

@router.get("/me", response_model=User)
@limiter.limit("5/minute")
async def me(request: Request, user: User = Depends(get_current_user)):
    """
       Retrieve the authenticated user's details.

       :param request: The incoming request object.
       :type request: Request
       :param user: The authenticated user.
       :type user: User
       :return: The authenticated user's details.
       :rtype: User
    """
    return user

@router.patch("/avatar", response_model=User)
async def update_avatar_user(
    file: UploadFile = File(),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
       Update the authenticated user's avatar.

       :param file: The uploaded avatar file.
       :type file: UploadFile
       :param user: The authenticated user.
       :type user: User
       :param db: Database session.
       :type db: AsyncSession
       :return: The updated user with the new avatar URL.
       :rtype: User
    """
    avatar_url = UploadFileService(
        settings.CLD_NAME, settings.CLD_API_KEY, settings.CLD_API_SECRET
    ).upload_file(file, user.username)

    user_service = UserService(db)
    user = await user_service.update_avatar_url(user.email, avatar_url)

    return user