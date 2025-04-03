"""
Authentication API
==================

This module provides authentication-related endpoints for user registration, login, email confirmation, and email verification requests.

Endpoints:
    - `/auth/register`: Register a new user.
    - `/auth/login`: Authenticate a user and return an access token.
    - `/auth/confirmed_email/{token}`: Confirm a user's email using a token.
    - `/auth/request_email`: Request an email verification link.

"""

from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from src.schemas import UserCreate, Token, User, RequestEmail
from src.services.auth import create_access_token, Hash, get_email_from_token
from src.services.email import send_email
from src.services.users import UserService
from src.database.db import get_db
from fastapi import APIRouter, HTTPException, Depends, status, Security, BackgroundTasks, Request

router = APIRouter(prefix="/auth", tags=["auth"])

# Реєстрація користувача
@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate, background_tasks: BackgroundTasks, request: Request, db: Session = Depends(get_db)):
    """
        Register a new user.

        :param user_data: User registration data.
        :type user_data: UserCreate
        :param background_tasks: Background task handler.
        :type background_tasks: BackgroundTasks
        :param request: FastAPI request instance.
        :type request: Request
        :param db: Database session dependency.
        :type db: Session
        :return: Newly registered user data.
        :rtype: User
        """
    user_service = UserService(db)

    email_user = await user_service.get_user_by_email(user_data.email)
    if email_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Користувач з таким email вже існує",
        )

    username_user = await user_service.get_user_by_username(user_data.username)
    if username_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Користувач з таким іменем вже існує",
        )
    user_data.password = Hash().get_password_hash(user_data.password)
    new_user = await user_service.create_user(user_data)
    background_tasks.add_task(
        send_email, new_user.email, new_user.username, request.base_url
    )

    return new_user

# Логін користувача
@router.post("/login", response_model=Token)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """
        Authenticate a user and return an access token.

        :param form_data: OAuth2 form data containing username and password.
        :type form_data: OAuth2PasswordRequestForm
        :param db: Database session dependency.
        :type db: Session
        :return: Access token and token type.
        :rtype: Token
        """
    user_service = UserService(db)
    user = await user_service.get_user_by_username(form_data.username)
    if not user or not Hash().verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неправильний логін або пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Електронна адреса не підтверджена",
        )

    access_token = await create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, db: Session = Depends(get_db)):
    """
        Confirm a user's email using a verification token.

        :param token: Verification token received via email.
        :type token: str
        :param db: Database session dependency.
        :type db: Session
        :return: Confirmation message.
        :rtype: dict
        """
    email = await get_email_from_token(token)
    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )
    if user.confirmed:
        return {"message": "Ваша електронна пошта вже підтверджена"}
    await user_service.confirmed_email(email)
    return {"message": "Електронну пошту підтверджено"}


@router.post("/request_email")
async def request_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    """
        Request an email verification link.

        :param body: Email request data.
        :type body: RequestEmail
        :param background_tasks: Background task handler.
        :type background_tasks: BackgroundTasks
        :param request: FastAPI request instance.
        :type request: Request
        :param db: Database session dependency.
        :type db: Session
        :return: Verification email sent message.
        :rtype: dict
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)

    if user.confirmed:
        return {"message": "Ваша електронна пошта вже підтверджена"}
    if user:
        background_tasks.add_task(
            send_email, user.email, user.username, request.base_url
        )
    return {"message": "Перевірте свою електронну пошту для підтвердження"}