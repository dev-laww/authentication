"""
Unit tests for HealthController.
"""

import pytest

from authentication.controllers.health import HealthController
from authentication.core.base.controller import Controller


# Fixtures
@pytest.fixture
def controller():
    """Create a HealthController instance."""
    return HealthController()


# Test check_health
@pytest.mark.asyncio
async def test_check_health_returns_healthy_status(controller):
    """check_health returns healthy status."""
    result = await controller.check_health()

    assert result == {"status": "healthy"}


@pytest.mark.asyncio
async def test_check_health_returns_dict(controller):
    """check_health returns a dictionary."""
    result = await controller.check_health()

    assert isinstance(result, dict)


@pytest.mark.asyncio
async def test_check_health_has_status_key(controller):
    """check_health response has status key."""
    result = await controller.check_health()

    assert "status" in result


@pytest.mark.asyncio
async def test_check_health_status_is_healthy(controller):
    """check_health status value is 'healthy'."""
    result = await controller.check_health()

    assert result["status"] == "healthy"


# Test controller inheritance
def test_health_controller_inherits_from_controller(controller):
    """HealthController inherits from Controller."""
    assert isinstance(controller, Controller)

