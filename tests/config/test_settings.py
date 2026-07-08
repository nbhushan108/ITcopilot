"""Settings loading and validation tests."""

import os

import pytest

from common.config.exceptions import ConfigurationError
from common.config.settings import (
    BaseAppSettings,
    DevelopmentSettings,
    Environment,
    ProductionSettings,
    TestingSettings,
    get_settings,
    load_settings,
    reset_settings_cache,
    resolve_settings_class,
)


@pytest.mark.unit
class TestSettingsProfiles:
    """Tests for environment-specific settings profiles."""

    def test_resolve_development_profile(self) -> None:
        """Development profile should be selected by name."""
        assert resolve_settings_class("development") is DevelopmentSettings

    def test_resolve_testing_profile(self) -> None:
        """Testing profile should be selected by name."""
        assert resolve_settings_class("testing") is TestingSettings

    def test_resolve_production_profile(self) -> None:
        """Production profile should be selected by name."""
        assert resolve_settings_class("production") is ProductionSettings

    def test_development_defaults(self) -> None:
        """Development settings should enable debug mode."""
        settings = DevelopmentSettings(
            secret_key="test-secret-key-not-for-production-use-only-32chars",
        )
        assert settings.debug is True
        assert settings.auth_enabled is False
        assert settings.log_json is False

    def test_testing_uses_in_memory_database(self) -> None:
        """Testing profile should default to in-memory SQLite."""
        settings = TestingSettings(
            secret_key="test-secret-key-not-for-production-use-only-32chars",
        )
        assert settings.database_url == "sqlite+aiosqlite:///:memory:"
        assert settings.auth_enabled is False

    def test_production_rejects_weak_secret(self) -> None:
        """Production should reject insecure secret keys."""
        with pytest.raises(ConfigurationError, match="SECRET_KEY"):
            ProductionSettings(
                secret_key="change-me-in-production",
                auth_admin_password_hash="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
            )

    def test_production_requires_admin_password_hash(self) -> None:
        """Production should require AUTH_ADMIN_PASSWORD_HASH."""
        with pytest.raises(ConfigurationError, match="AUTH_ADMIN_PASSWORD_HASH"):
            ProductionSettings(
                secret_key="a" * 32,
                auto_create_schema=False,
            )

    def test_jwt_secret_defaults_to_secret_key(self) -> None:
        """JWT secret should default to SECRET_KEY when unset."""
        settings = BaseAppSettings(
            environment=Environment.DEVELOPMENT,
            secret_key="test-secret-key-not-for-production-use-only-32chars",
        )
        assert settings.jwt_secret == settings.secret_key

    def test_cache_requires_cache_url(self) -> None:
        """Enabling cache without CACHE_URL should fail validation."""
        with pytest.raises(ConfigurationError, match="CACHE_URL"):
            BaseAppSettings(
                environment=Environment.DEVELOPMENT,
                secret_key="test-secret-key-not-for-production-use-only-32chars",
                enable_cache=True,
                cache_url=None,
            )

    def test_singleton_loader(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """get_settings should return cached singleton."""
        monkeypatch.setenv("ENVIRONMENT", "testing")
        monkeypatch.setenv("SECRET_KEY", "test-secret-key-not-for-production-use-only-32chars")
        reset_settings_cache()
        first = get_settings()
        second = get_settings()
        assert first is second
        reset_settings_cache()

    def test_load_settings_without_cache(self) -> None:
        """load_settings should create a fresh instance each call."""
        first = load_settings("testing")
        second = load_settings("testing")
        assert first is not second
        assert first.environment == Environment.TESTING

    def test_host_port_aliases(self) -> None:
        """HOST/PORT should map to host and port fields."""
        settings = BaseAppSettings(
            environment=Environment.DEVELOPMENT,
            host="127.0.0.1",
            port=9000,
            secret_key="test-secret-key-not-for-production-use-only-32chars",
        )
        assert settings.api_host == "127.0.0.1"
        assert settings.api_port == 9000

    def test_metadata_property(self) -> None:
        """Settings should expose resolved application metadata."""
        settings = BaseAppSettings(
            environment=Environment.DEVELOPMENT,
            app_name="ITcopilot",
            app_version="0.2.0",
            secret_key="test-secret-key-not-for-production-use-only-32chars",
        )
        assert settings.metadata.name == "ITcopilot"
        assert settings.metadata.version == "0.2.0"

    def teardown_method(self) -> None:
        """Reset settings cache after each test."""
        reset_settings_cache()
        os.environ.pop("ENVIRONMENT", None)
