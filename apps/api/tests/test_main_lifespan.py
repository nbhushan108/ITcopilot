"""Application lifespan and startup tests."""

import os

import pytest

from app.core.settings import Environment, Settings, get_settings
from app.db.session import reset_engine_cache
from app.main import create_app, lifespan


@pytest.mark.integration
class TestApplicationLifespan:
    """Tests for FastAPI application lifecycle."""

    @pytest.mark.asyncio
    async def test_lifespan_startup_and_shutdown(self) -> None:
        """Lifespan should complete startup and shutdown without error."""
        os.environ["ENVIRONMENT"] = "testing"
        os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
        os.environ["SECRET_KEY"] = "test-secret-key-not-for-production-use-only-32chars"
        os.environ["AUTO_CREATE_SCHEMA"] = "true"
        get_settings.cache_clear()
        reset_engine_cache()

        app = create_app()

        async with lifespan(app):
            assert app.title == "ITcopilot"

    def test_create_app_root_endpoint(self) -> None:
        """Root endpoint metadata should be present on the app."""
        settings = Settings(
            environment=Environment.TESTING,
            secret_key="test-secret-key-not-for-production-use-only-32chars",
            auth_admin_password="secret",
        )
        app = create_app(settings=settings)
        assert app.version == "0.1.0"
