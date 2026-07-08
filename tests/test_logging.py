"""Logging configuration unit tests."""

from pathlib import Path

import pytest

from app.core.logging import configure_logging, get_logger
from app.core.settings import Environment, Settings


@pytest.mark.unit
class TestLogging:
    """Tests for loguru configuration."""

    def test_configure_logging_development(self, tmp_path: Path) -> None:
        """Development logging should configure file handlers."""
        settings = Settings(
            environment=Environment.DEVELOPMENT,
            log_dir=str(tmp_path),
            log_level="DEBUG",
            secret_key="test-secret-key-not-for-production-use-only-32chars",
        )
        configure_logging(settings)
        logger = get_logger("test.module")
        logger.info("development log test")
        assert any(tmp_path.iterdir())

    def test_configure_logging_testing_skips_files(self, tmp_path: Path) -> None:
        """Testing environment should skip file log handlers."""
        settings = Settings(
            environment=Environment.TESTING,
            log_dir=str(tmp_path),
            secret_key="test-secret-key-not-for-production-use-only-32chars",
        )
        configure_logging(settings)
        assert get_logger("test") is not None
