"""Feature flag configuration tests."""

import pytest

from common.config.feature_flags import FeatureFlags
from common.config.settings import BaseAppSettings, Environment


@pytest.mark.unit
class TestFeatureFlags:
    """Tests for runtime feature flags."""

    def test_default_flags(self) -> None:
        """Default flags should match specification defaults."""
        flags = FeatureFlags()
        assert flags.enable_ai is False
        assert flags.enable_excel is True
        assert flags.enable_parser is True
        assert flags.enable_reports is True
        assert flags.enable_cache is False
        assert flags.enable_rest_api is True
        assert flags.enable_broker_import is True
        assert flags.enable_dashboard is True
        assert flags.enable_power_bi is False
        assert flags.enable_experimental is False

    def test_is_enabled_with_prefix(self) -> None:
        """is_enabled should accept feature names with enable_ prefix."""
        flags = FeatureFlags(enable_ai=True)
        assert flags.is_enabled("enable_ai") is True
        assert flags.is_enabled("ai") is True

    def test_is_enabled_unknown_feature(self) -> None:
        """Unknown features should return False."""
        flags = FeatureFlags()
        assert flags.is_enabled("unknown_module") is False

    def test_settings_feature_flags_property(self) -> None:
        """Settings should expose feature flags from environment fields."""
        settings = BaseAppSettings(
            environment=Environment.DEVELOPMENT,
            secret_key="test-secret-key-not-for-production-use-only-32chars",
            enable_ai=True,
            enable_experimental=True,
        )
        assert settings.feature_flags.enable_ai is True
        assert settings.feature_flags.enable_experimental is True
