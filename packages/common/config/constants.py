"""Shared configuration constants."""

from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parent.parent
PROJECT_ROOT = PACKAGE_ROOT.parent.parent

ENV_FILES: dict[str, str] = {
    "development": ".env.development",
    "testing": ".env.testing",
    "production": ".env.production",
}

DEFAULT_APP_NAME = "ITcopilot"
DEFAULT_APP_VERSION = "0.1.0"
DEFAULT_API_VERSION = "v1"
DEFAULT_BUILD_NUMBER = "0"
DEFAULT_RELEASE_DATE = "2026-07-08"

SUPPORTED_ASSESSMENT_YEARS: tuple[str, ...] = (
    "2023-24",
    "2024-25",
    "2025-26",
)

SUPPORTED_LOG_LEVELS: frozenset[str] = frozenset(
    {
        "TRACE",
        "DEBUG",
        "INFO",
        "SUCCESS",
        "WARNING",
        "ERROR",
        "CRITICAL",
    },
)

INSECURE_SECRET_KEYS: frozenset[str] = frozenset(
    {
        "change-me-in-production",
        "change-me-in-production-use-openssl-rand-hex-32",
        "test-secret-key-not-for-production",
        "changeme",
        "secret",
    },
)

DEFAULT_JWT_ALGORITHM = "HS256"
