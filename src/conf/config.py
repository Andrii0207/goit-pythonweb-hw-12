
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DB_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_SECONDS: int = 3600
    MAIL_USERNAME: str = "example@meta.ua",
    MAIL_PASSWORD: str = "secretPassword",
    MAIL_FROM: str = "example@meta.ua",
    MAIL_PORT: int = 465,
    MAIL_SERVER: str = "smtp.meta.ua",
    MAIL_FROM_NAME: str = "Example email",
    MAIL_STARTTLS: bool = False,
    MAIL_SSL_TLS: bool = True,
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True

    CLD_NAME: str = "cloudinary"
    CLD_API_KEY: int = 326488457974591
    CLD_API_SECRET: str = "secret"

    model_config = SettingsConfigDict(
        extra="ignore", env_file=".env", env_file_encoding="utf-8", case_sensitive=True
    )


settings = Settings()

