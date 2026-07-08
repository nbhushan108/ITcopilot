"""Configuration validator tests."""

import pytest

from common.config.exceptions import ConfigurationError
from common.config.validators import (
    validate_assessment_year,
    validate_database_url,
    validate_host,
    validate_log_level,
    validate_port,
    validate_required_variables,
    validate_tax_regime,
)


@pytest.mark.unit
class TestValidators:
    """Tests for configuration validators."""

    def test_validate_assessment_year_success(self) -> None:
        """Valid assessment year should pass."""
        assert validate_assessment_year("2025-26") == "2025-26"

    def test_validate_assessment_year_invalid_format(self) -> None:
        """Invalid format should raise ConfigurationError."""
        with pytest.raises(ConfigurationError, match="Invalid assessment year"):
            validate_assessment_year("2025")

    def test_validate_assessment_year_unsupported(self) -> None:
        """Unsupported year should raise ConfigurationError."""
        with pytest.raises(ConfigurationError, match="Unsupported assessment year"):
            validate_assessment_year("2019-20")

    def test_validate_tax_regime_success(self) -> None:
        """Valid regime should normalize to lowercase."""
        assert validate_tax_regime("OLD") == "old"

    def test_validate_tax_regime_invalid(self) -> None:
        """Invalid regime should raise ConfigurationError."""
        with pytest.raises(ConfigurationError, match="Invalid tax regime"):
            validate_tax_regime("flat")

    def test_validate_log_level_success(self) -> None:
        """Valid log level should uppercase."""
        assert validate_log_level("debug") == "DEBUG"

    def test_validate_log_level_invalid(self) -> None:
        """Invalid log level should raise ConfigurationError."""
        with pytest.raises(ConfigurationError, match="Invalid log level"):
            validate_log_level("verbose")

    def test_validate_host_success(self) -> None:
        """Valid host values should pass."""
        assert validate_host("0.0.0.0") == "0.0.0.0"
        assert validate_host("localhost") == "localhost"
        assert validate_host("127.0.0.1") == "127.0.0.1"

    def test_validate_host_invalid(self) -> None:
        """Invalid host should raise ConfigurationError."""
        with pytest.raises(ConfigurationError, match="Invalid host"):
            validate_host("not a host!")

    def test_validate_port_success(self) -> None:
        """Valid port should pass."""
        assert validate_port(8080) == 8080

    def test_validate_port_invalid(self) -> None:
        """Invalid port should raise ConfigurationError."""
        with pytest.raises(ConfigurationError, match="Invalid port"):
            validate_port(70000)

    def test_validate_database_url_invalid_scheme(self) -> None:
        """Unsupported database URL scheme should raise ConfigurationError."""
        with pytest.raises(ConfigurationError, match="Unsupported DATABASE_URL"):
            validate_database_url("invalid://not-a-real-driver")

    def test_validate_required_variables(self) -> None:
        """Missing required variables should raise ConfigurationError."""
        with pytest.raises(ConfigurationError, match="Missing required"):
            validate_required_variables({"SECRET_KEY": ""}, ("SECRET_KEY",))
