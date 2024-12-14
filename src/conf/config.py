from pydantic import ConfigDict, EmailStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application configuration settings loaded from environment variables or `.env` file.

    Attributes:
        DB_URL (str): The database connection URL.
        JWT_SECRET (str): The secret key for JWT encoding/decoding.
        JWT_ALGORITHM (str): The algorithm used for JWT. Defaults to "HS256".
        JWT_EXPIRATION_SECONDS (int): The expiration time for JWT tokens in seconds. Defaults to 3600.

        MAIL_USERNAME (EmailStr): The email address used for authentication with the mail server.
        MAIL_PASSWORD (str): The password for the mail server.
        MAIL_FROM (EmailStr): The sender email address for outgoing mails.
        MAIL_PORT (int): The port number of the mail server. Defaults to 465.
        MAIL_SERVER (str): The mail server address. Defaults to "smtp.meta.ua".
        MAIL_FROM_NAME (str): The display name for the mail sender. Defaults to "Rest API Service HW10".
        MAIL_STARTTLS (bool): Whether to use STARTTLS for mail server connection. Defaults to False.
        MAIL_SSL_TLS (bool): Whether to use SSL/TLS for mail server connection. Defaults to True.
        USE_CREDENTIALS (bool): Whether to use credentials for the mail server. Defaults to True.
        VALIDATE_CERTS (bool): Whether to validate certificates for the mail server connection. Defaults to True.

        CLD_NAME (str): The name of the Cloudinary account.
        CLD_API_KEY (int): The API key for Cloudinary.
        CLD_API_SECRET (str): The API secret for Cloudinary.

        REDIS_HOST (str): The Redis server host. Defaults to "localhost".
        REDIS_PASSWORD (str): The Redis server password.

        model_config (ConfigDict): The configuration for Pydantic settings, including `.env` file usage.
    """

    DB_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_SECONDS: int = 3600

    MAIL_USERNAME: EmailStr = "example@meta.ua"
    MAIL_PASSWORD: str = "secretPassword"
    MAIL_FROM: EmailStr = "example@meta.ua"
    MAIL_PORT: int = 465
    MAIL_SERVER: str = "smtp.meta.ua"
    MAIL_FROM_NAME: str = "Rest API Service HW10"
    MAIL_STARTTLS: bool = False
    MAIL_SSL_TLS: bool = True
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True

    CLD_NAME: str
    CLD_API_KEY: int = 111111111111111
    CLD_API_SECRET: str = "secret"

    REDIS_HOST: str = "localhost"
    REDIS_PASSWORD: str = "password"

    model_config = ConfigDict(
        extra="ignore", env_file=".env", env_file_encoding="utf-8", case_sensitive=True
    )


settings = Settings()
