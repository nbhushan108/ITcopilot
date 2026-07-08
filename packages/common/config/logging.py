"""Structured logging configuration using Loguru."""

import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any, Protocol

from loguru import logger

from common.config.types import LogLevel

if TYPE_CHECKING:
    from loguru import Logger


class LoggingSettingsProtocol(Protocol):
    """Minimal settings interface required for logging configuration."""

    log_level: LogLevel
    log_dir: str
    log_rotation: str
    log_retention: str
    log_compression: str
    log_json: bool
    environment: Any

    @property
    def is_development(self) -> bool:
        """Return True when running in development mode."""

    @property
    def is_testing(self) -> bool:
        """Return True when running in testing mode."""


def configure_logging(settings: LoggingSettingsProtocol) -> None:
    """Configure Loguru with console and rotating file handlers.

    Args:
        settings: Settings object exposing logging configuration fields.
    """
    logger.remove()

    console_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )

    logger.add(
        sys.stdout,
        level=settings.log_level,
        format=console_format,
        colorize=True,
        backtrace=settings.is_development,
        diagnose=settings.is_development,
    )

    if settings.is_testing:
        logger.info(
            "Logging configured for environment={} level={} (console only)",
            settings.environment,
            settings.log_level,
        )
        return

    log_dir = Path(settings.log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)

    text_format = (
        "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}"
    )

    if settings.log_json:
        logger.add(
            log_dir / "itcopilot_{time:YYYY-MM-DD}.log",
            level=settings.log_level,
            rotation="00:00",
            retention=settings.log_retention,
            compression=settings.log_compression,
            encoding="utf-8",
            backtrace=True,
            diagnose=False,
            serialize=True,
        )
        logger.add(
            log_dir / "itcopilot_errors.log",
            level="ERROR",
            rotation=settings.log_rotation,
            retention=settings.log_retention,
            compression=settings.log_compression,
            encoding="utf-8",
            backtrace=True,
            diagnose=True,
            serialize=True,
        )
    else:
        logger.add(
            log_dir / "itcopilot_{time:YYYY-MM-DD}.log",
            level=settings.log_level,
            format=text_format,
            rotation="00:00",
            retention=settings.log_retention,
            compression=settings.log_compression,
            encoding="utf-8",
            backtrace=True,
            diagnose=False,
        )
        logger.add(
            log_dir / "itcopilot_errors.log",
            level="ERROR",
            format=text_format,
            rotation=settings.log_rotation,
            retention=settings.log_retention,
            compression=settings.log_compression,
            encoding="utf-8",
            backtrace=True,
            diagnose=True,
        )

    logger.info(
        "Logging configured for environment={} level={} json={}",
        settings.environment,
        settings.log_level,
        settings.log_json,
    )


def get_logger(name: str) -> "Logger":
    """Return a logger instance bound to the given module name.

    Args:
        name: Module name for log context binding.

    Returns:
        Bound Loguru logger instance.
    """
    return logger.bind(module=name)
