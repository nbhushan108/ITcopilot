"""Custom application exceptions."""

from typing import Any


class ITcopilotError(Exception):
    """Base exception for all ITcopilot application errors."""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        """Initialize exception with message and optional details."""
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ConfigurationError(ITcopilotError):
    """Raised when application configuration is invalid."""


class DatabaseError(ITcopilotError):
    """Raised when a database operation fails."""


class NotFoundError(ITcopilotError):
    """Raised when a requested resource is not found."""


class ValidationError(ITcopilotError):
    """Raised when input validation fails at the service layer."""


class AuthenticationError(ITcopilotError):
    """Raised when authentication fails."""


class AuthorizationError(ITcopilotError):
    """Raised when authorization fails."""


class FileProcessingError(ITcopilotError):
    """Raised when file parsing or processing fails."""


class TaxComputationError(ITcopilotError):
    """Raised when tax computation encounters an error."""
