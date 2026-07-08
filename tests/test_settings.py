"""Production settings validation tests."""

import pytest

from app.core.exceptions import ConfigurationError
from app.core.settings import Environment, Settings


@pytest.mark.unit
class TestSettingsValidation:
    """Tests for settings validation rules."""

    def test_production_rejects_weak_secret(self) -> None:
        """Production should reject insecure secret keys."""
        with pytest.raises(ConfigurationError, match="SECRET_KEY"):
            Settings(
                environment=Environment.PRODUCTION,
                secret_key="change-me-in-production",
                debug=False,
                auto_create_schema=False,
            )

    def test_production_enables_auth(self) -> None:
        """Production should force auth enabled."""
        settings = Settings(
            environment=Environment.PRODUCTION,
            secret_key="a" * 32,
            debug=False,
            auto_create_schema=False,
            auth_admin_password_hash="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        )
        assert settings.auth_enabled is True

    def test_production_requires_admin_password_hash(self) -> None:
        """Production should require AUTH_ADMIN_PASSWORD_HASH."""
        with pytest.raises(ConfigurationError, match="AUTH_ADMIN_PASSWORD_HASH"):
            Settings(
                environment=Environment.PRODUCTION,
                secret_key="a" * 32,
                debug=False,
                auto_create_schema=False,
            )

    def test_testing_disables_auth(self) -> None:
        """Testing environment should disable auth by default."""
        settings = Settings(
            environment=Environment.TESTING,
            secret_key="test-secret-key-not-for-production-use-only-32chars",
        )
        assert settings.auth_enabled is False
        assert settings.auth_admin_password == "secret"

    def test_development_default_admin_password(self) -> None:
        """Development should default admin password when unset."""
        settings = Settings(
            environment=Environment.DEVELOPMENT,
            secret_key="test-secret-key-not-for-production-use-only-32chars",
        )
        assert settings.auth_admin_password == "secret"
