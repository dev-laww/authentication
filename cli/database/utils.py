from __future__ import annotations

import importlib
from functools import lru_cache
from pathlib import Path
from typing import Optional

from alembic.config import Config
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.schema import MetaData
from sqlmodel import SQLModel

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ALEMBIC_CONFIG_PATH = PROJECT_ROOT / "alembic.ini"
MIGRATIONS_PATH = PROJECT_ROOT / "migrations"
SEED_SCRIPT = PROJECT_ROOT / "scripts" / "seed.py"
DEFAULT_SCHEMA_SNAPSHOT = PROJECT_ROOT / "schema.snapshot.json"
SCHEMA_MODULE_ENV = "DATABASE_SCHEMA_MODULE"
DATABASE_URL_ENV = "DATABASE_URL"
DEFAULT_SCHEMA_MODULE = "authentication.models"


def ensure_alembic_is_configured() -> None:
    if not ALEMBIC_CONFIG_PATH.exists():
        raise FileNotFoundError(
            f"Alembic configuration not found at {ALEMBIC_CONFIG_PATH}. "
            "Run CLI commands from the project root or set ALEMBIC_CONFIG."
        )

    env_file = MIGRATIONS_PATH / "env.py"
    if not env_file.exists():
        raise FileNotFoundError(
            f"Alembic environment script not found at {env_file}. "
            "Ensure migrations/env.py exists."
        )


def build_alembic_config() -> Config:
    """
    Create an Alembic Config object pointing to the repository's migration setup.
    """

    ensure_alembic_is_configured()

    config = Config(str(ALEMBIC_CONFIG_PATH))
    config.set_main_option("script_location", str(MIGRATIONS_PATH))
    config.set_main_option("sqlalchemy.url", get_cli_settings().database_url)
    return config


def build_async_engine() -> AsyncEngine:
    """
    Create an async SQLAlchemy engine using the configured database URL.
    """

    url = make_url(get_cli_settings().database_url)
    if url.drivername.endswith("+asyncpg"):
        url = url.set(drivername="postgresql+asyncpg")

    return create_async_engine(str(url), future=True)


async def recreate_database() -> None:
    """
    Drop and recreate the configured database (development use only).
    """

    url = make_url(get_cli_settings().database_url)
    db_name = url.database
    admin_url = url.set(database="postgres")

    admin_engine = create_async_engine(
        str(admin_url), isolation_level="AUTOCOMMIT", future=True
    )

    async with admin_engine.begin() as conn:
        await conn.execute(
            text(
                """
                SELECT pg_terminate_backend(pid)
                FROM pg_stat_activity
                WHERE datname = :name
                  AND pid <> pg_backend_pid()
                """
            ),
            {"name": db_name},
        )
        await conn.execute(text(f'DROP DATABASE IF EXISTS "{db_name}"'))
        await conn.execute(text(f'CREATE DATABASE "{db_name}"'))

    await admin_engine.dispose()


def qualified_table_name(schema: str | None, name: str) -> str:
    if schema:
        return f'"{schema}"."{name}"'
    return f'"{name}"'


def default_schema_snapshot_path() -> Path:
    return DEFAULT_SCHEMA_SNAPSHOT


@lru_cache(maxsize=1)
def load_metadata() -> MetaData:
    """
    Import the configured schema module to register models, then return SQLModel.metadata.
    """

    settings = get_cli_settings()
    module_path = settings.schema_module or DEFAULT_SCHEMA_MODULE
    importlib.import_module(module_path)
    metadata = SQLModel.metadata

    if not isinstance(metadata, MetaData):
        raise TypeError("SQLModel.metadata is not a SQLAlchemy MetaData instance.")

    return metadata


class CLISettings(BaseSettings):
    database_url: str = Field(alias=DATABASE_URL_ENV)
    schema_module: Optional[str] = Field(alias=SCHEMA_MODULE_ENV)

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache(maxsize=1)
def get_cli_settings() -> CLISettings:
    return CLISettings()
