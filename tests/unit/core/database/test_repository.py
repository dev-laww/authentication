"""
Unit tests for Repository.
"""

import uuid
from unittest.mock import Mock, AsyncMock, patch

import pytest
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import SQLModel, Field
from sqlmodel.ext.asyncio.session import AsyncSession

from authentication.core.database.repository import Repository
from authentication.core.database.filters import gt, ilike, in_array
from authentication.core.exceptions import DatabaseError


# Test models
class SampleModel(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    age: int


# Fixtures
@pytest.fixture
def mock_session():
    """Create a mock AsyncSession."""
    session = Mock(spec=AsyncSession)
    session.add = Mock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.delete = AsyncMock()
    session.exec = AsyncMock()
    return session


@pytest.fixture
def repository(mock_session):
    """Create a Repository instance."""
    return Repository(mock_session, SampleModel)


# Test initialization
def test_repository_initialization(repository, mock_session):
    """Repository initializes with session and model."""
    assert repository.session == mock_session
    assert repository.model == SampleModel


# Test get
@pytest.mark.asyncio
async def test_get_retrieves_entity(repository, mock_session):
    """get retrieves an entity by ID."""
    entity_id = uuid.uuid4()
    mock_entity = SampleModel(id=entity_id, name="test", age=25)
    mock_result = Mock()
    mock_result.first.return_value = mock_entity
    mock_session.exec.return_value = mock_result

    result = await repository.get(entity_id)

    assert result == mock_entity
    mock_session.exec.assert_called_once()


@pytest.mark.asyncio
async def test_get_returns_none_when_not_found(repository, mock_session):
    """get returns None when entity not found."""
    entity_id = uuid.uuid4()
    mock_result = Mock()
    mock_result.first.return_value = None
    mock_session.exec.return_value = mock_result

    result = await repository.get(entity_id)

    assert result is None


@pytest.mark.asyncio
async def test_get_raises_database_error_on_failure(repository, mock_session):
    """get raises DatabaseError on SQLAlchemyError."""
    entity_id = uuid.uuid4()
    mock_session.exec.side_effect = SQLAlchemyError("Database error")

    with pytest.raises(DatabaseError):
        await repository.get(entity_id)


# Test get_or_raise
@pytest.mark.asyncio
async def test_get_or_raise_retrieves_entity(repository, mock_session):
    """get_or_raise retrieves an entity by ID."""
    entity_id = uuid.uuid4()
    mock_entity = SampleModel(id=entity_id, name="test", age=25)
    mock_result = Mock()
    mock_result.first.return_value = mock_entity
    mock_session.exec.return_value = mock_result

    result = await repository.get_or_raise(entity_id)

    assert result == mock_entity


@pytest.mark.asyncio
async def test_get_or_raise_raises_when_not_found(repository, mock_session):
    """get_or_raise raises DatabaseError when entity not found."""
    entity_id = uuid.uuid4()
    mock_result = Mock()
    mock_result.first.return_value = None
    mock_session.exec.return_value = mock_result

    with pytest.raises(DatabaseError, match="not found"):
        await repository.get_or_raise(entity_id)


# Test all
@pytest.mark.asyncio
async def test_all_retrieves_all_entities(repository, mock_session):
    """all retrieves all entities."""
    mock_entities = [
        SampleModel(id=uuid.uuid4(), name="test1", age=25),
        SampleModel(id=uuid.uuid4(), name="test2", age=30),
    ]
    mock_result = Mock()
    mock_result.all.return_value = mock_entities
    mock_session.exec.return_value = mock_result

    result = await repository.all()

    assert len(result) == 2
    assert result == mock_entities


@pytest.mark.asyncio
async def test_all_with_skip_and_limit(repository, mock_session):
    """all supports skip and limit parameters."""
    mock_entities = [SampleModel(id=uuid.uuid4(), name=f"test{i}", age=25) for i in range(5)]
    mock_result = Mock()
    mock_result.all.return_value = mock_entities[:3]
    mock_session.exec.return_value = mock_result

    result = await repository.all(skip=1, limit=3)

    assert len(result) == 3


@pytest.mark.asyncio
async def test_all_with_filters(repository, mock_session):
    """all supports filter parameters."""
    mock_entities = [SampleModel(id=uuid.uuid4(), name="test", age=25)]
    mock_result = Mock()
    mock_result.all.return_value = mock_entities
    mock_session.exec.return_value = mock_result

    result = await repository.all(name="test")

    assert len(result) == 1


@pytest.mark.asyncio
async def test_all_with_filter_objects(repository, mock_session):
    """all supports Filter objects."""
    mock_entities = [SampleModel(id=uuid.uuid4(), name="test", age=30)]
    mock_result = Mock()
    mock_result.all.return_value = mock_entities
    mock_session.exec.return_value = mock_result

    result = await repository.all(age=gt(25))

    assert len(result) == 1


@pytest.mark.asyncio
async def test_all_raises_database_error_on_failure(repository, mock_session):
    """all raises DatabaseError on SQLAlchemyError."""
    mock_session.exec.side_effect = SQLAlchemyError("Database error")

    with pytest.raises(DatabaseError):
        await repository.all()


# Test create
@pytest.mark.asyncio
async def test_create_creates_entity(repository, mock_session):
    """create creates a new entity."""
    entity = SampleModel(name="test", age=25)

    result = await repository.create(entity)

    assert result == entity
    mock_session.add.assert_called_once_with(entity)
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(entity)


@pytest.mark.asyncio
async def test_create_raises_database_error_on_failure(repository, mock_session):
    """create raises DatabaseError on SQLAlchemyError."""
    entity = SampleModel(name="test", age=25)
    mock_session.commit.side_effect = SQLAlchemyError("Database error")

    with pytest.raises(DatabaseError):
        await repository.create(entity)

    mock_session.rollback.assert_called_once()


# Test update
@pytest.mark.asyncio
async def test_update_updates_entity(repository, mock_session):
    """update updates an existing entity."""
    entity_id = uuid.uuid4()
    mock_entity = SampleModel(id=entity_id, name="old", age=25)
    mock_result = Mock()
    mock_result.first.return_value = mock_entity
    mock_session.exec.return_value = mock_result

    result = await repository.update(entity_id, name="new", age=30)

    assert result.name == "new"
    assert result.age == 30
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once()


@pytest.mark.asyncio
async def test_update_raises_on_invalid_attribute(repository, mock_session):
    """update raises ValueError for invalid attribute."""
    entity_id = uuid.uuid4()
    mock_entity = SampleModel(id=entity_id, name="test", age=25)
    mock_result = Mock()
    mock_result.first.return_value = mock_entity
    mock_session.exec.return_value = mock_result

    with pytest.raises(ValueError, match="Invalid update attribute"):
        await repository.update(entity_id, invalid_field="value")


@pytest.mark.asyncio
async def test_update_raises_database_error_on_failure(repository, mock_session):
    """update raises DatabaseError on SQLAlchemyError."""
    entity_id = uuid.uuid4()
    mock_entity = SampleModel(id=entity_id, name="test", age=25)
    mock_result = Mock()
    mock_result.first.return_value = mock_entity
    mock_session.exec.return_value = mock_result
    mock_session.commit.side_effect = SQLAlchemyError("Database error")

    with pytest.raises(DatabaseError):
        await repository.update(entity_id, name="new")

    mock_session.rollback.assert_called_once()


# Test delete
@pytest.mark.asyncio
async def test_delete_deletes_entity(repository, mock_session):
    """delete deletes an entity."""
    entity_id = uuid.uuid4()
    mock_entity = SampleModel(id=entity_id, name="test", age=25)
    mock_result = Mock()
    mock_result.first.return_value = mock_entity
    mock_session.exec.return_value = mock_result

    await repository.delete(entity_id)

    mock_session.delete.assert_called_once_with(mock_entity)
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_delete_raises_database_error_on_failure(repository, mock_session):
    """delete raises DatabaseError on SQLAlchemyError."""
    entity_id = uuid.uuid4()
    mock_entity = SampleModel(id=entity_id, name="test", age=25)
    mock_result = Mock()
    mock_result.first.return_value = mock_entity
    mock_session.exec.return_value = mock_result
    mock_session.commit.side_effect = SQLAlchemyError("Database error")

    with pytest.raises(DatabaseError):
        await repository.delete(entity_id)

    mock_session.rollback.assert_called_once()


# Test count
@pytest.mark.asyncio
async def test_count_returns_count(repository, mock_session):
    """count returns the number of entities."""
    mock_entities = [
        SampleModel(id=uuid.uuid4(), name="test1", age=25),
        SampleModel(id=uuid.uuid4(), name="test2", age=30),
    ]
    mock_result = Mock()
    mock_result.all.return_value = mock_entities
    mock_session.exec.return_value = mock_result

    result = await repository.count()

    assert result == 2


@pytest.mark.asyncio
async def test_count_with_filters(repository, mock_session):
    """count supports filter parameters."""
    mock_entities = [SampleModel(id=uuid.uuid4(), name="test", age=25)]
    mock_result = Mock()
    mock_result.all.return_value = mock_entities
    mock_session.exec.return_value = mock_result

    result = await repository.count(name="test")

    assert result == 1


# Test exists
@pytest.mark.asyncio
async def test_exists_returns_true_when_exists(repository, mock_session):
    """exists returns True when entity exists."""
    mock_entity = SampleModel(id=uuid.uuid4(), name="test", age=25)
    mock_result = Mock()
    mock_result.first.return_value = mock_entity
    mock_session.exec.return_value = mock_result

    result = await repository.exists(name="test")

    assert result is True


@pytest.mark.asyncio
async def test_exists_returns_false_when_not_exists(repository, mock_session):
    """exists returns False when entity doesn't exist."""
    mock_result = Mock()
    mock_result.first.return_value = None
    mock_session.exec.return_value = mock_result

    result = await repository.exists(name="nonexistent")

    assert result is False


@pytest.mark.asyncio
async def test_exists_raises_database_error_on_failure(repository, mock_session):
    """exists raises DatabaseError on SQLAlchemyError."""
    mock_session.exec.side_effect = SQLAlchemyError("Database error")

    with pytest.raises(DatabaseError):
        await repository.exists(name="test")


# Test _apply_filter
def test_apply_filter_with_plain_value(repository):
    """_apply_filter applies equality filter for plain values."""
    query = Mock()
    query.where = Mock(return_value=query)

    result = repository._apply_filter(query, "name", "test")

    query.where.assert_called_once()


def test_apply_filter_with_filter_object(repository):
    """_apply_filter applies Filter object."""
    query = Mock()
    query.where = Mock(return_value=query)
    filter_obj = gt(25)

    result = repository._apply_filter(query, "age", filter_obj)

    query.where.assert_called_once()


def test_apply_filter_raises_on_invalid_field(repository):
    """_apply_filter raises ValueError for invalid field."""
    query = Mock()

    with pytest.raises(ValueError, match="Invalid filter attribute"):
        repository._apply_filter(query, "invalid_field", "value")


# Test _apply_filters
def test_apply_filters_applies_multiple_filters(repository):
    """_apply_filters applies multiple filters."""
    query = Mock()
    query.where = Mock(return_value=query)

    result = repository._apply_filters(query, name="test", age=gt(25))

    assert query.where.call_count == 2

