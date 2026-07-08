"""Health service unit tests."""

import pytest

from app.core.settings import Environment, Settings
from app.services.health_service import HealthService


@pytest.mark.unit
class TestHealthService:
    """Tests for health check service."""

    @pytest.fixture
    def service(self) -> HealthService:
        """Provide health service with test settings."""
        settings = Settings(
            environment=Environment.TESTING,
            secret_key="test-secret-key-not-for-production-use-only-32chars",
        )
        return HealthService(settings=settings)

    @pytest.mark.asyncio
    async def test_get_health_delegates_to_readiness(self, service: HealthService) -> None:
        """get_health should return readiness response."""
        readiness = await service.get_readiness()
        health = await service.get_health()
        assert health.status == readiness.status
        assert health.checks == readiness.checks

    def test_get_version(self, service: HealthService) -> None:
        """Version response should include environment metadata."""
        version = service.get_version()
        assert version.name == "ITcopilot"
        assert version.environment == "testing"
