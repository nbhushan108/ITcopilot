"""FastAPI dependency injection unit tests."""

import pytest
from fastapi.security import HTTPAuthorizationCredentials

from app.core.dependencies import get_current_user, get_settings_dependency
from app.core.exceptions import AuthenticationError
from app.core.security import create_access_token
from app.core.settings import Environment, Settings


@pytest.mark.unit
class TestDependencies:
    """Tests for dependency providers."""

    @pytest.mark.asyncio
    async def test_get_settings_dependency(self) -> None:
        """Settings dependency should return application settings."""
        settings = await get_settings_dependency()
        assert settings.app_name == "ITcopilot"

    @pytest.mark.asyncio
    async def test_get_current_user_when_auth_disabled(self) -> None:
        """Auth disabled should return default user without credentials."""
        settings = Settings(
            environment=Environment.TESTING,
            auth_enabled=False,
            secret_key="test-secret-key-not-for-production-use-only-32chars",
        )
        user = await get_current_user(settings=settings, credentials=None)
        assert user.username == settings.auth_default_username

    @pytest.mark.asyncio
    async def test_get_current_user_requires_token_when_auth_enabled(self) -> None:
        """Auth enabled should reject missing credentials."""
        settings = Settings(
            environment=Environment.PRODUCTION,
            secret_key="a" * 32,
            debug=False,
            auto_create_schema=False,
            auth_enabled=True,
            auth_admin_password_hash="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        )
        with pytest.raises(AuthenticationError, match="Authentication required"):
            await get_current_user(settings=settings, credentials=None)

    @pytest.mark.asyncio
    async def test_get_current_user_with_valid_token(self) -> None:
        """Auth enabled should decode valid bearer tokens."""
        settings = Settings(
            environment=Environment.PRODUCTION,
            secret_key="a" * 32,
            debug=False,
            auto_create_schema=False,
            auth_enabled=True,
            auth_admin_password_hash="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        )
        token = create_access_token("admin", settings)
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        user = await get_current_user(settings=settings, credentials=credentials)
        assert user.username == "admin"
