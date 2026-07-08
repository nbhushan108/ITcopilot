"""Structured logging configuration using loguru."""

import sys
from pathlib import Path
from typing import TYPE_CHECKING

from loguru import logger

from app.core.settings import Settings


if TYPE_CHECKING:
    from loguru import Logger


def configure_logging(settings: Settings) -> None:
    """Configure loguru with console and rotating file handlers.

    Args:
        settings: Application settings containing log configuration.
    """
    logger.remove()

    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )

    logger.add(
        sys.stdout,
        level=settings.log_level,
        format=log_format,
        colorize=True,
        backtrace=settings.is_development,
        diagnose=settings.is_development,
    )

    if not settings.is_testing:
        log_dir = Path(settings.log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)

        logger.add(
            log_dir / "itcopilot_{time:YYYY-MM-DD}.log",
            level=settings.log_level,
            format=log_format,
            rotation=settings.log_rotation,
            retention=settings.log_retention,
            compression=settings.log_compression,
            encoding="utf-8",
            backtrace=True,
            diagnose=False,
        )

        logger.add(
            log_dir / "itcopilot_errors.log",
            level="ERROR",
            format=log_format,
            rotation=settings.log_rotation,
            retention=settings.log_retention,
            compression=settings.log_compression,
            encoding="utf-8",
            backtrace=True,
            diagnose=True,
        )

    logger.info(
        "Logging configured for environment={} level={}",
        settings.environment.value,
        settings.log_level,
    )


def get_logger(name: str) -> "Logger":
    """Return a logger instance bound to the given module name.

    Args:
        name: Module name for log context binding.

    Returns:
        Bound loguru logger instance.
    """
    return logger.bind(module=name)
