"""
Unit tests for DatabaseManager.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker

from authentication.core.database.manager import DatabaseManager, db_manager
from authentication.core.exceptions import DatabaseError


# Fixtures
@pytest.fixture
def manager():
    """Create a fresh DatabaseManager instance."""
    return DatabaseManager()


@pytest.fixture
def mock_settings():
    """Mock settings for database configuration."""
    with patch('authentication.core.database.manager.settings') as mock:
        mock.database_url = "sqlite+aiosqlite:///:memory:"
        mock.database_pool_size = 10
        mock.database_max_overflow = 20
        mock.database_pool_timeout = 30
        yield mock


# Test initialization
def test_database_manager_initialization(manager):
    """DatabaseManager initializes with None engine and session factory."""
    assert manager._engine is None
    assert manager._session_factory is None


# Test initialize
@patch('authentication.core.database.manager.create_async_engine')
@patch('authentication.core.database.manager.async_sessionmaker')
def test_initialize_creates_engine_and_session_factory(mock_sessionmaker, mock_create_engine, manager, mock_settings):
    """initialize creates engine and session factory."""
    mock_engine = Mock(spec=AsyncEngine)
    mock_factory = Mock(spec=async_sessionmaker)
    mock_create_engine.return_value = mock_engine
    mock_sessionmaker.return_value = mock_factory

    manager.initialize()

    assert manager._engine == mock_engine
    assert manager._session_factory == mock_factory
    mock_create_engine.assert_called_once()
    mock_sessionmaker.assert_called_once()


@patch('authentication.core.database.manager.create_async_engine')
@patch('authentication.core.database.manager.async_sessionmaker')
def test_initialize_raises_on_double_initialization(mock_sessionmaker, mock_create_engine, manager, mock_settings):
    """initialize raises RuntimeError if already initialized."""
    mock_engine = Mock(spec=AsyncEngine)
    mock_factory = Mock(spec=async_sessionmaker)
    mock_create_engine.return_value = mock_engine
    mock_sessionmaker.return_value = mock_factory

    manager.initialize()

    with pytest.raises(RuntimeError, match="already initialized"):
        manager.initialize()


@patch('authentication.core.database.manager.create_async_engine')
def test_initialize_raises_database_error_on_failure(mock_create_engine, manager, mock_settings):
    """initialize raises DatabaseError on initialization failure."""
    mock_create_engine.side_effect = Exception("Connection failed")

    with pytest.raises(DatabaseError, match="Failed to initialize database"):
        manager.initialize()


# Test get_session
@pytest.mark.asyncio
async def test_get_session_raises_when_not_initialized(manager):
    """get_session raises RuntimeError when not initialized."""
    with pytest.raises(RuntimeError, match="not initialized"):
        async with manager.get_session():
            pass


@pytest.mark.asyncio
async def test_get_session_provides_session(manager):
    """get_session provides a database session."""
    mock_session = AsyncMock()
    mock_factory = Mock()
    mock_context = AsyncMock()
    mock_context.__aenter__ = AsyncMock(return_value=mock_session)
    mock_context.__aexit__ = AsyncMock(return_value=None)
    mock_factory.return_value = mock_context

    manager._session_factory = mock_factory

    async with manager.get_session() as session:
        assert session == mock_session


@pytest.mark.asyncio
async def test_get_session_rolls_back_on_error(manager):
    """get_session rolls back on error."""
    mock_session = AsyncMock()
    mock_session.rollback = AsyncMock()
    mock_factory = Mock()
    mock_context = AsyncMock()
    mock_context.__aenter__ = AsyncMock(return_value=mock_session)
    mock_context.__aexit__ = AsyncMock(return_value=None)
    mock_factory.return_value = mock_context

    manager._session_factory = mock_factory

    with pytest.raises(ValueError):
        async with manager.get_session():
            raise ValueError("Test error")

    mock_session.rollback.assert_called_once()


@pytest.mark.asyncio
async def test_get_session_raises_database_error_on_sqlalchemy_error(manager):
    """get_session raises DatabaseError on SQLAlchemyError."""
    mock_session = AsyncMock()
    mock_session.rollback = AsyncMock()
    mock_factory = Mock()
    mock_context = AsyncMock()
    mock_context.__aenter__ = AsyncMock(return_value=mock_session)
    mock_context.__aexit__ = AsyncMock(return_value=None)
    mock_factory.return_value = mock_context

    manager._session_factory = mock_factory

    with pytest.raises(DatabaseError):
        async with manager.get_session():
            raise SQLAlchemyError("Database error")


@pytest.mark.asyncio
async def test_get_session_closes_session(manager):
    """get_session closes session after use."""
    mock_session = AsyncMock()
    mock_session.close = AsyncMock()
    mock_factory = Mock()
    mock_context = AsyncMock()
    mock_context.__aenter__ = AsyncMock(return_value=mock_session)
    mock_context.__aexit__ = AsyncMock(return_value=None)
    mock_factory.return_value = mock_context

    manager._session_factory = mock_factory

    async with manager.get_session():
        pass

    mock_session.close.assert_called_once()


# Test session_dependency
@pytest.mark.asyncio
async def test_session_dependency_provides_session(manager):
    """session_dependency provides a database session."""
    mock_session = AsyncMock()
    mock_factory = Mock()
    mock_context = AsyncMock()
    mock_context.__aenter__ = AsyncMock(return_value=mock_session)
    mock_context.__aexit__ = AsyncMock(return_value=None)
    mock_factory.return_value = mock_context

    manager._session_factory = mock_factory

    async for session in manager.session_dependency():
        assert session == mock_session
        break


# Test with_session decorator
@pytest.mark.asyncio
async def test_with_session_decorator_injects_session(manager):
    """with_session decorator injects session into function."""
    mock_session = AsyncMock()
    mock_factory = Mock()
    mock_context = AsyncMock()
    mock_context.__aenter__ = AsyncMock(return_value=mock_session)
    mock_context.__aexit__ = AsyncMock(return_value=None)
    mock_factory.return_value = mock_context

    manager._session_factory = mock_factory

    @manager.with_session
    async def test_function(db):
        return db

    result = await test_function()
    assert result == mock_session


@pytest.mark.asyncio
async def test_with_session_decorator_preserves_function_signature(manager):
    """with_session decorator preserves function signature."""
    mock_session = AsyncMock()
    mock_factory = Mock()
    mock_context = AsyncMock()
    mock_context.__aenter__ = AsyncMock(return_value=mock_session)
    mock_context.__aexit__ = AsyncMock(return_value=None)
    mock_factory.return_value = mock_context

    manager._session_factory = mock_factory

    @manager.with_session
    async def test_function(param1, param2, db):
        return param1 + param2

    result = await test_function(1, 2)
    assert result == 3


# Test dispose
@pytest.mark.asyncio
async def test_dispose_disposes_engine(manager):
    """dispose disposes the database engine."""
    mock_engine = Mock(spec=AsyncEngine)
    mock_engine.dispose = AsyncMock()
    manager._engine = mock_engine

    await manager.dispose()

    mock_engine.dispose.assert_called_once()
    assert manager._engine is None
    assert manager._session_factory is None


@pytest.mark.asyncio
async def test_dispose_raises_when_not_initialized(manager):
    """dispose raises RuntimeError when not initialized."""
    with pytest.raises(RuntimeError, match="not initialized"):
        await manager.dispose()


# Test engine property
def test_engine_property_returns_engine(manager):
    """engine property returns the database engine."""
    mock_engine = Mock(spec=AsyncEngine)
    manager._engine = mock_engine

    assert manager.engine == mock_engine


def test_engine_property_raises_when_not_initialized(manager):
    """engine property raises RuntimeError when not initialized."""
    with pytest.raises(RuntimeError, match="not initialized"):
        _ = manager.engine


# Test session_factory property
def test_session_factory_property_returns_factory(manager):
    """session_factory property returns the session factory."""
    mock_factory = Mock(spec=async_sessionmaker)
    manager._session_factory = mock_factory

    assert manager.session_factory == mock_factory


def test_session_factory_property_raises_when_not_initialized(manager):
    """session_factory property raises RuntimeError when not initialized."""
    with pytest.raises(RuntimeError, match="not initialized"):
        _ = manager.session_factory


# Test db_manager singleton
def test_db_manager_is_singleton():
    """db_manager is a singleton instance."""
    from authentication.core.database.manager import (
        db_manager as db_manager_1,
        db_manager as db_manager_2,
    )

    assert db_manager_1 is db_manager_2

