"""
Unit tests for utility generators.
"""

import datetime
from unittest.mock import patch

import pytest

from authentication.core.utils.generators import get_current_utc_datetime


# Test get_current_utc_datetime
def test_get_current_utc_datetime_returns_datetime():
    """get_current_utc_datetime returns datetime object."""
    result = get_current_utc_datetime()

    assert isinstance(result, datetime.datetime)


def test_get_current_utc_datetime_is_timezone_aware():
    """get_current_utc_datetime returns timezone-aware datetime."""
    result = get_current_utc_datetime()

    assert result.tzinfo is not None


def test_get_current_utc_datetime_is_utc():
    """get_current_utc_datetime returns UTC datetime."""
    result = get_current_utc_datetime()

    # Check that timezone is UTC
    assert result.tzinfo.utcoffset(None).total_seconds() == 0


@patch('authentication.core.utils.generators.arrow.utcnow')
def test_get_current_utc_datetime_uses_arrow(mock_utcnow):
    """get_current_utc_datetime uses arrow.utcnow."""
    mock_datetime = datetime.datetime.now(datetime.timezone.utc)
    mock_utcnow.return_value.datetime = mock_datetime

    result = get_current_utc_datetime()

    assert result == mock_datetime
    mock_utcnow.assert_called_once()


def test_get_current_utc_datetime_returns_current_time():
    """get_current_utc_datetime returns approximately current time."""
    before = datetime.datetime.now(datetime.timezone.utc)
    result = get_current_utc_datetime()
    after = datetime.datetime.now(datetime.timezone.utc)

    assert before <= result <= after

