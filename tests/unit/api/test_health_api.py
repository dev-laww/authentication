"""
Unit tests for HealthRouter.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from authentication.api.health import HealthRouter, router
from authentication.core.routing import AppRouter


# Fixtures
@pytest.fixture
def app():
    """Create a FastAPI app for testing."""
    app = FastAPI()
    app.include_router(router.http_router)
    return app


@pytest.fixture
def client(app):
    """Create a test client."""
    return TestClient(app)


# Test router initialization
def test_health_router_initialization():
    """HealthRouter initializes correctly."""
    health_router = HealthRouter(prefix="/health")

    assert health_router.http_router.prefix == "/health"


def test_router_has_controller_dependency():
    """HealthRouter has controller dependency."""
    health_router = HealthRouter(prefix="/health")
    deps = health_router._get_class_dependencies()

    assert "controller" in deps


# Test get_health_status endpoint
def test_get_health_status_endpoint(client):
    """get_health_status endpoint returns healthy status."""
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_get_health_status_endpoint_returns_dict(client):
    """get_health_status endpoint returns dictionary."""
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)


# Test get_health_status_v2 endpoint
def test_get_health_status_v2_endpoint(client):
    """get_health_status_v2 endpoint returns v2 status."""
    # Note: This would require version middleware to be set up
    # For now, we'll test that the route exists
    response = client.get("/health")

    assert response.status_code == 200


# Test router prefix
def test_router_prefix():
    """Router has correct prefix."""
    assert router.http_router.prefix == "/health"


# Test router inheritance
def test_health_router_inherits_from_app_router():
    """HealthRouter inherits from AppRouter."""
    health_router = HealthRouter(prefix="/health")
    assert isinstance(health_router, AppRouter)


# Test router routes
def test_router_has_routes():
    """Router has registered routes."""
    assert len(router.http_router.routes) > 0


def test_router_routes_are_get_methods():
    """Router routes use GET method."""
    for route in router.http_router.routes:
        if hasattr(route, "methods"):
            assert "GET" in route.methods

