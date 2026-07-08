"""Enterprise configuration settings with environment profiles."""

import json
import os
import secrets
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import AliasChoices, Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from common.config.constants import (
    DEFAULT_JWT_ALGORITHM,
    ENV_FILES,
    INSECURE_SECRET_KEYS,
)
from common.config.exceptions import ConfigurationError
from common.config.feature_flags import FeatureFlags
from common.config.metadata import ApplicationMetadata
from common.config.tax_config import get_tax_year_config
from common.config.types import Environment, LogLevel, TaxRegimeName
from common.config.validators import (
    validate_assessment_year,
    validate_database_url,
    validate_host,
    validate_log_level,
    validate_port,
    validate_required_variables,
    validate_tax_regime,
)


def _resolve_env_file() -> str | None:
    """Resolve environment-specific dotenv file based on ENVIRONMENT variable."""
    environment = os.getenv("ENVIRONMENT", "development").lower()
    env_file = ENV_FILES.get(environment)
    if env_file and Path(env_file).exists():
        return env_file
    if Path(".env").exists():
        return ".env"
    return None


class BaseAppSettings(BaseSettings):
    """Shared application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=_resolve_env_file(),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        populate_by_name=True,
    )

    app_name: str = Field(default="ITcopilot", validation_alias=AliasChoices("APP_NAME"))
    app_version: str = Field(default="0.1.0", validation_alias=AliasChoices("APP_VERSION"))
    api_version: str = Field(default="v1", validation_alias=AliasChoices("API_VERSION"))
    environment: Environment = Field(default=Environment.DEVELOPMENT)
    debug: bool = Field(default=False)
    build_number: str = Field(default="0")
    release_date: str = Field(default="2026-07-08")

    host: str = Field(
        default="0.0.0.0",
        validation_alias=AliasChoices("HOST", "API_HOST"),
    )
    port: int = Field(
        default=8000,
        ge=1,
        le=65535,
        validation_alias=AliasChoices("PORT", "API_PORT"),
    )
    api_prefix: str = Field(default="/api/v1")
    api_workers: int = Field(default=1, ge=1)

    database_url: str = Field(default="sqlite+aiosqlite:///./data/itcopilot.db")
    database_echo: bool = Field(default=False)
    database_pool_size: int = Field(default=5, ge=1)
    database_max_overflow: int = Field(default=10, ge=0)
    auto_create_schema: bool = Field(default=True)

    log_level: LogLevel = Field(default="INFO")
    log_dir: str = Field(default="logs")
    log_rotation: str = Field(default="10 MB")
    log_retention: str = Field(default="30 days")
    log_compression: str = Field(default="zip")
    log_json: bool = Field(default=True)

    secret_key: str = Field(default="change-me-in-production")
    jwt_secret: str | None = Field(default=None)
    jwt_algorithm: str = Field(default=DEFAULT_JWT_ALGORITHM)

    enable_ai: bool = Field(default=False)
    enable_excel: bool = Field(default=True)
    enable_parser: bool = Field(default=True)
    enable_reports: bool = Field(default=True)
    enable_cache: bool = Field(default=False)
    enable_rest_api: bool = Field(default=True)
    enable_broker_import: bool = Field(default=True)
    enable_dashboard: bool = Field(default=True)
    enable_power_bi: bool = Field(default=False)
    enable_experimental: bool = Field(default=False)
    cache_url: str | None = Field(default=None)

    tax_assessment_year: str = Field(default="2025-26")
    tax_regime: TaxRegimeName = Field(default="old")

    cors_origins: list[str] = Field(
        default=["http://localhost:5173", "http://localhost:3000"],
    )
    cors_allow_credentials: bool = Field(default=True)

    access_token_expire_minutes: int = Field(default=30, ge=1)
    auth_enabled: bool = Field(default=False)
    auth_default_username: str = Field(default="admin")
    auth_admin_password: str | None = Field(default=None)
    auth_admin_password_hash: str | None = Field(default=None)

    max_upload_size_mb: int = Field(default=50, ge=1)
    upload_dir: str = Field(default="uploads")

    @field_validator("log_level", mode="before")
    @classmethod
    def normalize_log_level(cls, value: str) -> str:
        """Normalize and validate log level."""
        return validate_log_level(str(value))

    @field_validator("host", mode="before")
    @classmethod
    def normalize_host(cls, value: str) -> str:
        """Validate host binding."""
        return validate_host(str(value))

    @field_validator("port", mode="before")
    @classmethod
    def normalize_port(cls, value: int | str) -> int:
        """Validate TCP port."""
        return validate_port(int(value))

    @field_validator("database_url", mode="after")
    @classmethod
    def normalize_database_url(cls, value: str) -> str:
        """Validate database URL scheme."""
        return validate_database_url(value)

    @field_validator("tax_assessment_year", mode="before")
    @classmethod
    def normalize_assessment_year(cls, value: str) -> str:
        """Validate configured default assessment year."""
        return validate_assessment_year(str(value))

    @field_validator("tax_regime", mode="before")
    @classmethod
    def normalize_tax_regime(cls, value: str) -> str:
        """Validate configured default tax regime."""
        return validate_tax_regime(str(value))

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        """Parse CORS origins from JSON array, comma-separated string, or list."""
        if isinstance(value, list):
            return value
        stripped = value.strip()
        if stripped.startswith(("[", "{")):
            try:
                parsed = json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise ConfigurationError("CORS_ORIGINS contains invalid JSON") from exc
            if not isinstance(parsed, list):
                raise ConfigurationError("CORS_ORIGINS JSON value must be an array")
            return [str(origin).strip() for origin in parsed if str(origin).strip()]
        return [origin.strip() for origin in value.split(",") if origin.strip()]

    @model_validator(mode="after")
    def finalize_settings(self) -> "BaseAppSettings":
        """Apply cross-field validation and derived defaults."""
        if not self.jwt_secret:
            object.__setattr__(self, "jwt_secret", self.secret_key)

        if self.environment == Environment.PRODUCTION:
            validate_required_variables(
                {
                    "SECRET_KEY": self.secret_key,
                    "DATABASE_URL": self.database_url,
                },
                ("SECRET_KEY", "DATABASE_URL"),
            )
            if self.secret_key in INSECURE_SECRET_KEYS or len(self.secret_key) < 32:
                raise ConfigurationError(
                    "Production requires a secure SECRET_KEY (min 32 chars). "
                    "Generate with: openssl rand -hex 32",
                )
            if self.debug:
                raise ConfigurationError("DEBUG must be false in production")
            if self.auto_create_schema:
                raise ConfigurationError(
                    "AUTO_CREATE_SCHEMA must be false in production; use Alembic migrations",
                )
            if not self.auth_admin_password_hash:
                raise ConfigurationError(
                    "AUTH_ADMIN_PASSWORD_HASH is required in production.",
                )
            object.__setattr__(self, "auth_enabled", True)
        elif self.environment == Environment.TESTING:
            object.__setattr__(self, "auth_enabled", False)
            object.__setattr__(self, "auto_create_schema", True)
            if not self.auth_admin_password_hash and not self.auth_admin_password:
                object.__setattr__(self, "auth_admin_password", "secret")
        elif not self.auth_admin_password_hash and not self.auth_admin_password:
            object.__setattr__(self, "auth_admin_password", "secret")

        if self.enable_cache and not self.cache_url:
            raise ConfigurationError("CACHE_URL is required when ENABLE_CACHE is true")

        get_tax_year_config(self.tax_assessment_year)
        return self

    @property
    def is_development(self) -> bool:
        """Return True when running in development mode."""
        return self.environment == Environment.DEVELOPMENT

    @property
    def is_testing(self) -> bool:
        """Return True when running in testing mode."""
        return self.environment == Environment.TESTING

    @property
    def is_production(self) -> bool:
        """Return True when running in production mode."""
        return self.environment == Environment.PRODUCTION

    @property
    def api_host(self) -> str:
        """Backward-compatible alias for host binding."""
        return self.host

    @property
    def api_port(self) -> int:
        """Backward-compatible alias for port binding."""
        return self.port

    @property
    def max_upload_size_bytes(self) -> int:
        """Return maximum upload size in bytes."""
        return self.max_upload_size_mb * 1024 * 1024

    @property
    def metadata(self) -> ApplicationMetadata:
        """Return resolved application metadata."""
        return ApplicationMetadata.from_environment(
            app_name=self.app_name,
            app_version=self.app_version,
            api_version=self.api_version,
            build_number=self.build_number,
            release_date=self.release_date,
        )

    @property
    def feature_flags(self) -> FeatureFlags:
        """Return resolved feature flag configuration."""
        return FeatureFlags.from_environment(
            enable_ai=self.enable_ai,
            enable_excel=self.enable_excel,
            enable_parser=self.enable_parser,
            enable_reports=self.enable_reports,
            enable_cache=self.enable_cache,
            enable_rest_api=self.enable_rest_api,
            enable_broker_import=self.enable_broker_import,
            enable_dashboard=self.enable_dashboard,
            enable_power_bi=self.enable_power_bi,
            enable_experimental=self.enable_experimental,
        )

    def generate_secret_key(self) -> str:
        """Generate a cryptographically secure secret key."""
        return secrets.token_hex(32)


class DevelopmentSettings(BaseAppSettings):
    """Development environment settings profile."""

    model_config = SettingsConfigDict(
        env_file=".env.development",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        populate_by_name=True,
    )

    environment: Literal[Environment.DEVELOPMENT] = Environment.DEVELOPMENT
    debug: bool = True
    auth_enabled: bool = False
    auto_create_schema: bool = True
    log_json: bool = False


class TestingSettings(BaseAppSettings):
    """Testing environment settings profile."""

    __test__ = False

    model_config = SettingsConfigDict(
        env_file=".env.testing",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        populate_by_name=True,
    )

    environment: Literal[Environment.TESTING] = Environment.TESTING
    debug: bool = True
    auth_enabled: bool = False
    auto_create_schema: bool = True
    database_url: str = "sqlite+aiosqlite:///:memory:"
    log_json: bool = False


class ProductionSettings(BaseAppSettings):
    """Production environment settings profile."""

    model_config = SettingsConfigDict(
        env_file=".env.production",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        populate_by_name=True,
    )

    environment: Literal[Environment.PRODUCTION] = Environment.PRODUCTION
    debug: bool = False
    auth_enabled: bool = True
    auto_create_schema: bool = False
    log_json: bool = True


Settings = BaseAppSettings

_SETTINGS_CLASS_MAP: dict[str, type[BaseAppSettings]] = {
    Environment.DEVELOPMENT.value: DevelopmentSettings,
    Environment.TESTING.value: TestingSettings,
    Environment.PRODUCTION.value: ProductionSettings,
}


def resolve_settings_class(environment: str | None = None) -> type[BaseAppSettings]:
    """Resolve the settings class for an environment name.

    Args:
        environment: Optional environment override. Defaults to ``ENVIRONMENT`` env var.

    Returns:
        Settings class for the requested environment.
    """
    env_name = (environment or os.getenv("ENVIRONMENT") or Environment.DEVELOPMENT.value).lower()
    return _SETTINGS_CLASS_MAP.get(env_name, DevelopmentSettings)


def load_settings(environment: str | None = None) -> BaseAppSettings:
    """Load settings for the requested environment without caching.

    Args:
        environment: Optional environment override.

    Returns:
        Instantiated settings object for the environment profile.
    """
    settings_class = resolve_settings_class(environment)
    return settings_class()


@lru_cache
def get_settings() -> BaseAppSettings:
    """Return cached application settings singleton."""
    return load_settings()


def reset_settings_cache() -> None:
    """Clear cached settings singleton (primarily for tests)."""
    get_settings.cache_clear()
