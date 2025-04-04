"""
Configuration Settings
======================

This module defines the configuration settings for the application, including database, authentication,
and email service configurations.

Configuration Variables:
    - `DB_URL` (str): Database connection URL.
    - `JWT_SECRET` (str): Secret key for JWT authentication.
    - `JWT_ALGORITHM` (str): Algorithm used for JWT tokens (default: "HS256").
    - `JWT_EXPIRATION_SECONDS` (int): Expiration time for JWT tokens in seconds (default: 3600).
    - `MAIL_USERNAME` (str): Email service username.
    - `MAIL_PASSWORD` (str): Email service password.
    - `MAIL_FROM` (str): Sender email address.
    - `MAIL_PORT` (int): Email server port (default: 465).
    - `MAIL_SERVER` (str): SMTP server address (default: "smtp.meta.ua").
    - `MAIL_FROM_NAME` (str): Sender name.
    - `MAIL_STARTTLS` (bool): Whether to use STARTTLS (default: False).
    - `MAIL_SSL_TLS` (bool): Whether to use SSL/TLS (default: True).
    - `USE_CREDENTIALS` (bool): Whether to use authentication credentials (default: True).
    - `VALIDATE_CERTS` (bool): Whether to validate email certificates (default: True).
    - `CLD_NAME` (str): Cloudinary cloud name (default: "cloudinary").
    - `CLD_API_KEY` (int): Cloudinary API key.
    - `CLD_API_SECRET` (str): Cloudinary API secret.

Environment Configuration:
    - The settings are loaded from a `.env` file.
    - The configuration is case-sensitive.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DB_URL: str = "postgresql+asyncpg://user:pass@localhost:5432/db_name"
    JWT_SECRET: str = "secret_key"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_SECONDS: int = 3600
    MAIL_USERNAME: str = "example@meta.ua"
    MAIL_PASSWORD: str = "secretPassword"
    MAIL_FROM: str = "example@meta.ua"
    MAIL_PORT: int = 465
    MAIL_SERVER: str = "smtp.meta.ua"
    MAIL_FROM_NAME: str = "Example email"
    MAIL_STARTTLS: bool = False
    MAIL_SSL_TLS: bool = True
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True
    JWT_REFRESH_SECRET: str="secret_refresh_code"

    CLD_NAME: str = "cloudinary"
    CLD_API_KEY: int = 326488457974591
    CLD_API_SECRET: str = "secret"

    model_config = SettingsConfigDict(
        extra="ignore", env_file=".env", env_file_encoding="utf-8", case_sensitive=True
    )


settings = Settings()

