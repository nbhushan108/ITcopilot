"""Configuration-specific exceptions."""


class ConfigurationError(Exception):
    """Raised when application configuration is invalid or incomplete."""

    def __init__(self, message: str) -> None:
        """Initialize configuration error with a descriptive message.

        Args:
            message: Human-readable explanation of the configuration failure.
        """
        super().__init__(message)
        self.message = message
