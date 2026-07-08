"""Application metadata tests."""

from datetime import date

import pytest

from common.config.metadata import ApplicationMetadata, get_application_metadata


@pytest.mark.unit
class TestApplicationMetadata:
    """Tests for application metadata resolution."""

    def test_default_metadata(self) -> None:
        """Default metadata should include core fields."""
        metadata = ApplicationMetadata()
        assert metadata.name == "ITcopilot"
        assert metadata.version == "0.1.0"
        assert metadata.license == "Apache-2.0"
        assert metadata.repository_url.endswith("ITcopilot")

    def test_from_environment_overrides(self) -> None:
        """Environment overrides should replace defaults."""
        metadata = ApplicationMetadata.from_environment(
            app_name="Custom",
            app_version="1.2.3",
            build_number="42",
            release_date="2026-01-01",
        )
        assert metadata.name == "Custom"
        assert metadata.version == "1.2.3"
        assert metadata.build_number == "42"
        assert metadata.release_date == date(2026, 1, 1)

    def test_metadata_singleton(self) -> None:
        """get_application_metadata should return cached metadata."""
        get_application_metadata.cache_clear()
        first = get_application_metadata()
        second = get_application_metadata()
        assert first is second
