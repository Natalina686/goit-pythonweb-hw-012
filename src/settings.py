from pydantic import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Attributes:
        POSTGRES_USER (str): PostgreSQL username.
        POSTGRES_PASSWORD (str): PostgreSQL password.
        POSTGRES_DB (str): PostgreSQL database name.
        DATABASE_URL (str): Full database connection URL.

        SECRET_KEY (str): Secret key for JWT encoding/decoding.
        ALGORITHM (str): JWT algorithm, e.g., HS256.
        ACCESS_TOKEN_EXPIRE_MINUTES (int): Token expiration in minutes.

        CLOUDINARY_CLOUD_NAME (str): Cloudinary cloud name for file uploads.
        CLOUDINARY_API_KEY (str): Cloudinary API key.
        CLOUDINARY_API_SECRET (str): Cloudinary API secret.

        FRONTEND_URL (str): Frontend base URL for generating links.
    """

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DATABASE_URL: str

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    CLOUDINARY_CLOUD_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str

    FRONTEND_URL: str

    class Config:
        """Configuration for Pydantic settings to load from .env file."""
        env_file = ".env"


settings = Settings()
