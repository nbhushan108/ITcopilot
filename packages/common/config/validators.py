"""Configuration validation helpers."""

import ipaddress
import re
from typing import cast
from urllib.parse import urlparse

from common.config.constants import SUPPORTED_ASSESSMENT_YEARS, SUPPORTED_LOG_LEVELS
from common.config.exceptions import ConfigurationError
from common.config.types import TaxRegimeName

HOST_PATTERN = re.compile(
    r"^(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)$|^localhost$|^[a-zA-Z0-9.-]+$",
)


def validate_required_variables(
    values: dict[str, str | None],
    required: tuple[str, ...],
) -> None:
    """Ensure required environment variables are present and non-empty.

    Args:
        values: Mapping of variable names to resolved values.
        required: Variable names that must be set.

    Raises:
        ConfigurationError: If any required variable is missing or blank.
    """
    missing = [name for name in required if not values.get(name)]
    if missing:
        joined = ", ".join(missing)
        raise ConfigurationError(f"Missing required environment variables: {joined}")


def validate_assessment_year(assessment_year: str) -> str:
    """Validate an Indian assessment year identifier.

    Args:
        assessment_year: Assessment year in ``YYYY-YY`` format.

    Returns:
        The validated assessment year string.

    Raises:
        ConfigurationError: If the year format or value is unsupported.
    """
    if not re.fullmatch(r"^\d{4}-\d{2}$", assessment_year):
        raise ConfigurationError(
            f"Invalid assessment year format: {assessment_year!r}. Expected YYYY-YY.",
        )
    if assessment_year not in SUPPORTED_ASSESSMENT_YEARS:
        supported = ", ".join(SUPPORTED_ASSESSMENT_YEARS)
        raise ConfigurationError(
            f"Unsupported assessment year: {assessment_year!r}. Supported: {supported}",
        )
    return assessment_year


def validate_tax_regime(regime: str) -> TaxRegimeName:
    """Validate a tax regime identifier.

    Args:
        regime: Tax regime name.

    Returns:
        Normalized regime value.

    Raises:
        ConfigurationError: If the regime is not ``old`` or ``new``.
    """
    normalized = regime.lower().strip()
    if normalized not in {"old", "new"}:
        raise ConfigurationError(f"Invalid tax regime: {regime!r}. Expected 'old' or 'new'.")
    return cast("TaxRegimeName", normalized)


def validate_log_level(level: str) -> str:
    """Validate a Loguru log level name.

    Args:
        level: Log level string.

    Returns:
        Uppercase log level.

    Raises:
        ConfigurationError: If the level is not recognized.
    """
    normalized = level.upper().strip()
    if normalized not in SUPPORTED_LOG_LEVELS:
        supported = ", ".join(sorted(SUPPORTED_LOG_LEVELS))
        raise ConfigurationError(f"Invalid log level: {level!r}. Supported: {supported}")
    return normalized


def validate_host(host: str) -> str:
    """Validate a network host binding value.

    Args:
        host: Hostname or IP address.

    Returns:
        Validated host string.

    Raises:
        ConfigurationError: If the host value is invalid.
    """
    candidate = host.strip()
    if not candidate:
        raise ConfigurationError("HOST must not be empty.")

    if candidate == "0.0.0.0":
        return candidate

    try:
        ipaddress.ip_address(candidate)
        return candidate
    except ValueError:
        pass

    if HOST_PATTERN.fullmatch(candidate):
        return candidate

    raise ConfigurationError(f"Invalid host: {host!r}")


def validate_port(port: int) -> int:
    """Validate a TCP port number.

    Args:
        port: Port number.

    Returns:
        Validated port number.

    Raises:
        ConfigurationError: If the port is outside the valid range.
    """
    if port < 1 or port > 65535:
        raise ConfigurationError(f"Invalid port: {port}. Must be between 1 and 65535.")
    return port


def validate_database_url(database_url: str) -> str:
    """Validate a SQLAlchemy database URL.

    Args:
        database_url: Database connection URL.

    Returns:
        Validated database URL.

    Raises:
        ConfigurationError: If the URL scheme is unsupported.
    """
    parsed = urlparse(database_url)
    if parsed.scheme not in {
        "sqlite",
        "sqlite+aiosqlite",
        "postgresql",
        "postgresql+asyncpg",
    }:
        raise ConfigurationError(
            f"Unsupported DATABASE_URL scheme: {parsed.scheme!r}",
        )
    return database_url
