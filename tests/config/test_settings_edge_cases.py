"""Additional settings edge-case tests."""

import json
from importlib.metadata import PackageNotFoundError
from pathlib import Path
from unittest.mock import patch

import pytest

from common.config.constants import DEFAULT_APP_VERSION
from common.config.exceptions import ConfigurationError
from common.config.metadata import _resolve_package_version
from common.config.settings import (
    BaseAppSettings,
    DevelopmentSettings,
    Environment,
    ProductionSettings,
    _resolve_env_file,
    resolve_settings_class,
)


@pytest.mark.unit
class TestSettingsEdgeCases:
    """Tests for settings validation edge cases and env resolution."""

    def test_cors_origins_json_array(self) -> None:
        """CORS_ORIGINS JSON array strings should parse correctly."""
        origins_json = json.dumps(
            ["http://localhost:5173", "http://localhost:3000"],
        )
        settings = BaseAppSettings(
            environment=Environment.DEVELOPMENT,
            cors_origins=origins_json,
            secret_key="test-secret-key-not-for-production-use-only-32chars",
        )
        assert settings.cors_origins == [
            "http://localhost:5173",
            "http://localhost:3000",
        ]

    def test_cors_origins_comma_separated(self) -> None:
        """CORS_ORIGINS comma-separated strings should parse correctly."""
        settings = BaseAppSettings(
            environment=Environment.DEVELOPMENT,
            cors_origins="http://a.example, http://b.example",
            secret_key="test-secret-key-not-for-production-use-only-32chars",
        )
        assert settings.cors_origins == ["http://a.example", "http://b.example"]

    def test_cors_origins_invalid_json(self) -> None:
        """Invalid CORS_ORIGINS JSON should raise ConfigurationError."""
        with pytest.raises(ConfigurationError, match="invalid JSON"):
            BaseAppSettings(
                environment=Environment.DEVELOPMENT,
                cors_origins='["unclosed"',
                secret_key="test-secret-key-not-for-production-use-only-32chars",
            )

    def test_cors_origins_json_not_array(self) -> None:
        """Non-array CORS_ORIGINS JSON should raise ConfigurationError."""
        with pytest.raises(ConfigurationError, match="must be an array"):
            BaseAppSettings(
                environment=Environment.DEVELOPMENT,
                cors_origins='{"not": "array"}',
                secret_key="test-secret-key-not-for-production-use-only-32chars",
            )

    def test_production_rejects_debug(self) -> None:
        """Production should reject DEBUG=true."""
        with pytest.raises(ConfigurationError, match="DEBUG must be false"):
            ProductionSettings(
                secret_key="a" * 32,
                debug=True,
                auto_create_schema=False,
                auth_admin_password_hash="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
            )

    def test_production_rejects_auto_create_schema(self) -> None:
        """Production should reject AUTO_CREATE_SCHEMA=true."""
        with pytest.raises(ConfigurationError, match="AUTO_CREATE_SCHEMA"):
            ProductionSettings(
                secret_key="a" * 32,
                debug=False,
                auto_create_schema=True,
                auth_admin_password_hash="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
            )

    def test_development_default_admin_password(self) -> None:
        """Development should default admin password when unset."""
        settings = BaseAppSettings(
            environment=Environment.DEVELOPMENT,
            secret_key="test-secret-key-not-for-production-use-only-32chars",
        )
        assert settings.auth_admin_password == "secret"

    def test_generate_secret_key(self) -> None:
        """generate_secret_key should return a 64-char hex string."""
        settings = BaseAppSettings(
            environment=Environment.DEVELOPMENT,
            secret_key="test-secret-key-not-for-production-use-only-32chars",
        )
        generated = settings.generate_secret_key()
        assert len(generated) == 64
        assert all(char in "0123456789abcdef" for char in generated)

    def test_resolve_settings_unknown_environment(self) -> None:
        """Unknown environment names should fall back to DevelopmentSettings."""
        assert resolve_settings_class("staging") is DevelopmentSettings

    def test_resolve_env_file_returns_none_without_files(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        """_resolve_env_file should return None when no env files exist."""
        monkeypatch.chdir(tmp_path)
        monkeypatch.setenv("ENVIRONMENT", "development")
        assert _resolve_env_file() is None

    def test_metadata_package_not_found_fallback(self) -> None:
        """Metadata should fall back to default version when package is missing."""
        with patch(
            "common.config.metadata.pkg_version",
            side_effect=PackageNotFoundError("itcopilot"),
        ):
            assert _resolve_package_version() == DEFAULT_APP_VERSION
