"""
Unit tests for database filter utilities.
"""

import pytest
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import declarative_base

from authentication.core.database.filters import (
    Filter,
    GreaterThan,
    GreaterThanOrEqual,
    LessThan,
    LessThanOrEqual,
    NotEqual,
    Like,
    ILike,
    In,
    NotIn,
    IsNull,
    IsNotNull,
    gt,
    gte,
    lt,
    lte,
    ne,
    like,
    ilike,
    in_array,
    not_in_array,
    is_null,
    is_not_null,
)

Base = declarative_base()


class SampleModel(Base):
    __tablename__ = "sample_model"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    age = Column(Integer)
    score = Column(Integer)


# Test Filter base class
def test_filter_is_abstract():
    """Filter is an abstract base class."""
    with pytest.raises(TypeError):
        Filter()


# Test GreaterThan
def test_greater_than_filter():
    """GreaterThan filter creates > condition."""
    filter_obj = GreaterThan(10)
    condition = filter_obj.apply(SampleModel.age)

    assert str(condition) == "sample_model.age > :age_1"


def test_gt_function():
    """gt function creates GreaterThan filter."""
    filter_obj = gt(10)
    assert isinstance(filter_obj, GreaterThan)
    assert filter_obj.value == 10


# Test GreaterThanOrEqual
def test_greater_than_or_equal_filter():
    """GreaterThanOrEqual filter creates >= condition."""
    filter_obj = GreaterThanOrEqual(10)
    condition = filter_obj.apply(SampleModel.age)

    assert ">=" in str(condition)


def test_gte_function():
    """gte function creates GreaterThanOrEqual filter."""
    filter_obj = gte(10)
    assert isinstance(filter_obj, GreaterThanOrEqual)
    assert filter_obj.value == 10


# Test LessThan
def test_less_than_filter():
    """LessThan filter creates < condition."""
    filter_obj = LessThan(10)
    condition = filter_obj.apply(SampleModel.age)

    assert "<" in str(condition)


def test_lt_function():
    """lt function creates LessThan filter."""
    filter_obj = lt(10)
    assert isinstance(filter_obj, LessThan)
    assert filter_obj.value == 10


# Test LessThanOrEqual
def test_less_than_or_equal_filter():
    """LessThanOrEqual filter creates <= condition."""
    filter_obj = LessThanOrEqual(10)
    condition = filter_obj.apply(SampleModel.age)

    assert "<=" in str(condition)


def test_lte_function():
    """lte function creates LessThanOrEqual filter."""
    filter_obj = lte(10)
    assert isinstance(filter_obj, LessThanOrEqual)
    assert filter_obj.value == 10


# Test NotEqual
def test_not_equal_filter():
    """NotEqual filter creates != condition."""
    filter_obj = NotEqual("test")
    condition = filter_obj.apply(SampleModel.name)

    assert "!=" in str(condition) or "<>" in str(condition)


def test_ne_function():
    """ne function creates NotEqual filter."""
    filter_obj = ne("test")
    assert isinstance(filter_obj, NotEqual)
    assert filter_obj.value == "test"


# Test Like
def test_like_filter():
    """Like filter creates LIKE condition."""
    filter_obj = Like("%test%")
    condition = filter_obj.apply(SampleModel.name)

    assert "LIKE" in str(condition).upper()


def test_like_function():
    """like function creates Like filter."""
    filter_obj = like("%test%")
    assert isinstance(filter_obj, Like)
    assert filter_obj.pattern == "%test%"


# Test ILike
def test_ilike_filter():
    """ILike filter creates ILIKE condition."""
    filter_obj = ILike("%test%")
    condition = filter_obj.apply(SampleModel.name)

    # SQLAlchemy uses LOWER() LIKE LOWER() for case-insensitive matching
    condition_str = str(condition).upper()
    assert "LIKE" in condition_str and "LOWER" in condition_str


def test_ilike_function():
    """ilike function creates ILike filter."""
    filter_obj = ilike("%test%")
    assert isinstance(filter_obj, ILike)
    assert filter_obj.pattern == "%test%"


# Test In
def test_in_filter_with_list():
    """In filter creates IN condition with list."""
    filter_obj = In([1, 2, 3])
    condition = filter_obj.apply(SampleModel.id)

    assert "IN" in str(condition).upper()


def test_in_filter_with_tuple():
    """In filter creates IN condition with tuple."""
    filter_obj = In((1, 2, 3))
    condition = filter_obj.apply(SampleModel.id)

    assert "IN" in str(condition).upper()


def test_in_filter_raises_on_invalid_type():
    """In filter raises ValueError for invalid type."""
    with pytest.raises(ValueError, match="requires a list or tuple"):
        In("not a list")


def test_in_array_function():
    """in_array function creates In filter."""
    filter_obj = in_array([1, 2, 3])
    assert isinstance(filter_obj, In)
    assert filter_obj.values == [1, 2, 3]


# Test NotIn
def test_not_in_filter():
    """NotIn filter creates NOT IN condition."""
    filter_obj = NotIn([1, 2, 3])
    condition = filter_obj.apply(SampleModel.id)

    assert "NOT" in str(condition).upper() and "IN" in str(condition).upper()


def test_not_in_filter_raises_on_invalid_type():
    """NotIn filter raises ValueError for invalid type."""
    with pytest.raises(ValueError, match="requires a list or tuple"):
        NotIn("not a list")


def test_not_in_array_function():
    """not_in_array function creates NotIn filter."""
    filter_obj = not_in_array([1, 2, 3])
    assert isinstance(filter_obj, NotIn)
    assert filter_obj.values == [1, 2, 3]


# Test IsNull
def test_is_null_filter():
    """IsNull filter creates IS NULL condition."""
    filter_obj = IsNull()
    condition = filter_obj.apply(SampleModel.name)

    assert "IS" in str(condition).upper() and "NULL" in str(condition).upper()


def test_is_null_function():
    """is_null function creates IsNull filter."""
    filter_obj = is_null()
    assert isinstance(filter_obj, IsNull)


# Test IsNotNull
def test_is_not_null_filter():
    """IsNotNull filter creates IS NOT NULL condition."""
    filter_obj = IsNotNull()
    condition = filter_obj.apply(SampleModel.name)

    assert "IS" in str(condition).upper() and "NOT" in str(condition).upper() and "NULL" in str(condition).upper()


def test_is_not_null_function():
    """is_not_null function creates IsNotNull filter."""
    filter_obj = is_not_null()
    assert isinstance(filter_obj, IsNotNull)


# Test filter application with different field types
def test_filter_with_string_field():
    """Filters work with string fields."""
    filter_obj = Like("%test%")
    condition = filter_obj.apply(SampleModel.name)

    assert condition is not None


def test_filter_with_integer_field():
    """Filters work with integer fields."""
    filter_obj = gt(10)
    condition = filter_obj.apply(SampleModel.age)

    assert condition is not None


# Test filter values
def test_filter_stores_value():
    """Filters store their values correctly."""
    filter_obj = gt(42)
    assert filter_obj.value == 42

    filter_obj = Like("%pattern%")
    assert filter_obj.pattern == "%pattern%"

    filter_obj = In([1, 2, 3])
    assert filter_obj.values == [1, 2, 3]


# Test edge cases
def test_in_filter_with_empty_list():
    """In filter handles empty list."""
    filter_obj = In([])
    condition = filter_obj.apply(SampleModel.id)

    assert condition is not None


def test_in_filter_with_single_value():
    """In filter handles single value."""
    filter_obj = In([1])
    condition = filter_obj.apply(SampleModel.id)

    assert condition is not None


def test_like_filter_with_wildcards():
    """Like filter handles various wildcard patterns."""
    patterns = ["%test%", "test%", "%test", "test_", "_test"]

    for pattern in patterns:
        filter_obj = Like(pattern)
        condition = filter_obj.apply(SampleModel.name)
        assert condition is not None


def test_ilike_filter_case_insensitive():
    """ILike filter is case-insensitive."""
    filter_obj = ILike("%TEST%")
    condition = filter_obj.apply(SampleModel.name)

    # SQLAlchemy uses LOWER() LIKE LOWER() for case-insensitive matching
    condition_str = str(condition).upper()
    assert "LIKE" in condition_str and "LOWER" in condition_str


# Test numeric comparisons
def test_numeric_filters_with_float():
    """Numeric filters work with float values."""
    filter_obj = gt(10.5)
    assert filter_obj.value == 10.5

    filter_obj = lt(20.5)
    assert filter_obj.value == 20.5


def test_numeric_filters_with_negative():
    """Numeric filters work with negative values."""
    filter_obj = gt(-10)
    assert filter_obj.value == -10

    filter_obj = lt(-5)
    assert filter_obj.value == -5


# Test string comparisons
def test_string_filters():
    """String filters work correctly."""
    filter_obj = ne("test")
    assert filter_obj.value == "test"

    filter_obj = Like("test%")
    assert filter_obj.pattern == "test%"

