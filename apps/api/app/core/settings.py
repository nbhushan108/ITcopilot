"""Application configuration using pydantic-settings."""

import secrets
from enum import StrEnum
from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.exceptions import ConfigurationError


INSECURE_SECRET_KEYS: frozenset[str] = frozenset(
    {
        "change-me-in-production",
        "change-me-in-production-use-openssl-rand-hex-32",
        "test-secret-key-not-for-production",
        "changeme",
        "secret",
    },
)


class Environment(StrEnum):
    """Supported deployment environments."""

    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = Field(default="ITcopilot", description="Application display name")
    app_version: str = Field(default="0.1.0", description="Semantic version")
    environment: Environment = Field(default=Environment.DEVELOPMENT)
    debug: bool = Field(default=False, description="Enable debug mode")

    # API
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000, ge=1, le=65535)
    api_prefix: str = Field(default="/api/v1")
    api_workers: int = Field(default=1, ge=1)

    # CORS
    cors_origins: list[str] = Field(
        default=["http://localhost:5173", "http://localhost:3000"],
    )
    cors_allow_credentials: bool = Field(default=True)

    # Database
    database_url: str = Field(default="sqlite+aiosqlite:///./data/itcopilot.db")
    database_echo: bool = Field(default=False)
    database_pool_size: int = Field(default=5, ge=1)
    database_max_overflow: int = Field(default=10, ge=0)
    auto_create_schema: bool = Field(
        default=True,
        description="Auto-create tables on startup (dev/test only; use Alembic in production)",
    )

    # Logging
    log_level: Literal["TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
    )
    log_dir: str = Field(default="logs")
    log_rotation: str = Field(default="10 MB")
    log_retention: str = Field(default="30 days")
    log_compression: str = Field(default="zip")

    # Security / Auth
    secret_key: str = Field(default="change-me-in-production")
    access_token_expire_minutes: int = Field(default=30, ge=1)
    auth_enabled: bool = Field(
        default=False,
        description="Require JWT authentication on protected routes",
    )
    auth_default_username: str = Field(
        default="admin",
        description="Default username for development token issuance",
    )
    auth_admin_password: str | None = Field(
        default=None,
        description="Plain admin password for dev/test token endpoint only",
    )
    auth_admin_password_hash: str | None = Field(
        default=None,
        description="Bcrypt hash for admin token endpoint (required in production)",
    )

    # Tax Engine
    tax_assessment_year: str = Field(default="2025-26")
    tax_regime: Literal["old", "new"] = Field(default="old")

    # File Processing
    max_upload_size_mb: int = Field(default=50, ge=1)
    upload_dir: str = Field(default="uploads")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        """Parse CORS origins from comma-separated string or JSON list."""
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @model_validator(mode="after")
    def validate_production_settings(self) -> "Settings":
        """Enforce secure configuration in production."""
        if self.environment == Environment.PRODUCTION:
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
                    "AUTH_ADMIN_PASSWORD_HASH is required in production. "
                    "Generate a bcrypt hash with hash_password() from app.core.security.",
                )
            object.__setattr__(self, "auth_enabled", True)
        elif self.environment == Environment.TESTING:
            object.__setattr__(self, "auth_enabled", False)
            object.__setattr__(self, "auto_create_schema", True)
            if not self.auth_admin_password_hash and not self.auth_admin_password:
                object.__setattr__(self, "auth_admin_password", "secret")
        elif not self.auth_admin_password_hash and not self.auth_admin_password:
            object.__setattr__(self, "auth_admin_password", "secret")
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
    def max_upload_size_bytes(self) -> int:
        """Return maximum upload size in bytes."""
        return self.max_upload_size_mb * 1024 * 1024

    def generate_secret_key(self) -> str:
        """Generate a cryptographically secure secret key."""
        return secrets.token_hex(32)


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings singleton."""
    return Settings()
