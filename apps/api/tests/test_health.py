"""Health endpoint integration tests."""

import pytest
from httpx import AsyncClient


@pytest.mark.integration
class TestHealthEndpoint:
    """Tests for health and version endpoints."""

    async def test_health_returns_200(self, client: AsyncClient) -> None:
        """Health endpoint should return HTTP 200."""
        response = await client.get("/api/v1/health")
        assert response.status_code == 200

    async def test_health_response_schema(self, client: AsyncClient) -> None:
        """Health response should contain required fields and database check."""
        response = await client.get("/api/v1/health")
        data = response.json()

        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert data["environment"] == "testing"
        assert "version" in data
        assert "checks" in data
        assert data["checks"]["database"]["status"] == "healthy"

    async def test_liveness_returns_200(self, client: AsyncClient) -> None:
        """Liveness endpoint should return HTTP 200."""
        response = await client.get("/api/v1/health/live")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    async def test_readiness_returns_200(self, client: AsyncClient) -> None:
        """Readiness endpoint should return HTTP 200."""
        response = await client.get("/api/v1/health/ready")
        assert response.status_code == 200
        assert response.json()["checks"]["database"]["status"] == "healthy"

    async def test_version_returns_200(self, client: AsyncClient) -> None:
        """Version endpoint should return HTTP 200."""
        response = await client.get("/api/v1/version")
        assert response.status_code == 200

    async def test_version_response_schema(self, client: AsyncClient) -> None:
        """Version response should contain required fields."""
        response = await client.get("/api/v1/version")
        data = response.json()

        assert data["name"] == "ITcopilot"
        assert data["version"] == "0.1.0"
        assert data["api_prefix"] == "/api/v1"
        assert data["environment"] == "testing"

    async def test_root_endpoint(self, client: AsyncClient) -> None:
        """Root endpoint should return welcome message."""
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "docs" in data

    async def test_openapi_docs_available(self, client: AsyncClient) -> None:
        """OpenAPI schema should be accessible."""
        response = await client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        assert schema["info"]["title"] == "ITcopilot"
