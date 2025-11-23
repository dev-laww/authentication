from enum import Enum
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(Enum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"


class DatabaseSettings(BaseSettings):
    url: str = Field(..., description="Database connection URL")
    pool_size: int = Field(default=10, description="Database connection pool size")
    max_overflow: int = Field(
        default=20, description="Maximum overflow size for the database connection pool"
    )
    pool_timeout: int = Field(
        default=30,
        description="Timeout for acquiring a database connection from the pool in seconds",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="DATABASE_",
        env_ignore_empty=True,
        env_file_encoding="utf-8",
        extra="ignore",
    )


class AppSettings(BaseSettings):
    name: str = Field(
        default="Authentication Service", description="The name of the application"
    )
    version: str = Field(default="1.0.0", description="The version of the application")
    description: str = Field(
        default="Service for user authentication and management",
        description="The description of the application",
    )
    default_api_version: str = Field(
        default="latest", description="The default API version for the application"
    )
    jwt_secret: str = Field(..., description="Secret key used for JWT token generation")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="APP_",
        env_ignore_empty=True,
        env_file_encoding="utf-8",
        extra="ignore",
    )


class ResendSettings(BaseSettings):
    api_key: str = Field(..., description="API key for Resend email service")
    email_from: str = Field(
        description="Default 'from' email address for sending emails",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="RESEND_",
        env_ignore_empty=True,
        env_file_encoding="utf-8",
        extra="ignore",
    )


class Settings(BaseSettings):
    environment: Environment = Field(
        default=Environment.DEVELOPMENT, description="The application environment"
    )
    debug: bool = Field(default=False, description="Enable or disable debug mode")

    enable_api_docs: bool = Field(
        default=True, description="Enable or disable API documentation endpoints"
    )
    redoc_url: str = Field(
        default="/redoc", description="URL path for ReDoc documentation"
    )
    docs_url: str = Field(
        default="/docs", description="URL path for Swagger UI documentation"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def is_production(self) -> bool:
        return self.environment == Environment.PRODUCTION

    @property
    def is_development(self) -> bool:
        return self.environment == Environment.DEVELOPMENT


class Config:
    def __init__(self):
        self.database = DatabaseSettings()
        self.resend = ResendSettings()
        self.app = AppSettings()
        self.settings = Settings()


@lru_cache
def get_config() -> Config:
    return Config()


settings = get_config()
