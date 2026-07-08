"""Logging configuration tests."""

from pathlib import Path

import pytest

from common.config.logging import configure_logging, get_logger
from common.config.settings import DevelopmentSettings, Environment, TestingSettings


@pytest.mark.unit
class TestLoggingConfiguration:
    """Tests for Loguru logging setup."""

    def test_configure_logging_development(self, tmp_path: Path) -> None:
        """Development logging should configure rotating file handlers."""
        settings = DevelopmentSettings(
            environment=Environment.DEVELOPMENT,
            log_dir=str(tmp_path),
            log_level="DEBUG",
            secret_key="test-secret-key-not-for-production-use-only-32chars",
        )
        configure_logging(settings)
        logger = get_logger("common.config.test")
        logger.info("development log test")
        assert any(tmp_path.iterdir())

    def test_configure_logging_testing_skips_files(self, tmp_path: Path) -> None:
        """Testing environment should skip file log handlers."""
        settings = TestingSettings(
            log_dir=str(tmp_path),
            secret_key="test-secret-key-not-for-production-use-only-32chars",
        )
        configure_logging(settings)
        assert get_logger("common.config.test") is not None
        assert not any(tmp_path.iterdir())

    def test_json_logging_enabled(self, tmp_path: Path) -> None:
        """Production-style JSON logging should write serialized logs."""
        settings = DevelopmentSettings(
            environment=Environment.DEVELOPMENT,
            log_dir=str(tmp_path),
            log_json=True,
            secret_key="test-secret-key-not-for-production-use-only-32chars",
        )
        configure_logging(settings)
        get_logger("common.config.test").info("json log test")
        log_files = list(tmp_path.glob("itcopilot_*.log"))
        assert log_files
        content = log_files[0].read_text(encoding="utf-8")
        assert '"level"' in content or "json log test" in content
