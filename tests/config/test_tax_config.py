"""Tax configuration tests."""

from decimal import Decimal

import pytest

from common.config.exceptions import ConfigurationError
from common.config.tax_config import (
    TAX_YEAR_CONFIGURATIONS,
    TaxRegime,
    get_default_tax_config,
    get_tax_year_config,
)
from common.config.types import ResidentStatus


@pytest.mark.unit
class TestTaxConfiguration:
    """Tests for tax year configuration registry."""

    def test_supported_years_registered(self) -> None:
        """Built-in assessment years should be available."""
        assert "2023-24" in TAX_YEAR_CONFIGURATIONS
        assert "2024-25" in TAX_YEAR_CONFIGURATIONS
        assert "2025-26" in TAX_YEAR_CONFIGURATIONS

    def test_get_tax_year_config(self) -> None:
        """Should return configuration for supported year."""
        config = get_tax_year_config("2025-26")
        assert config.assessment_year == "2025-26"
        assert config.financial_year == "2024-25"
        assert config.resident_status == ResidentStatus.RESIDENT

    def test_get_tax_year_config_invalid(self) -> None:
        """Invalid year should raise ConfigurationError."""
        with pytest.raises(ConfigurationError):
            get_tax_year_config("2018-19")

    def test_default_tax_config_is_latest(self) -> None:
        """Default config should resolve to latest supported year."""
        latest = max(TAX_YEAR_CONFIGURATIONS)
        assert get_default_tax_config().assessment_year == latest

    def test_regime_slabs(self) -> None:
        """Old and new regime slabs should differ."""
        config = get_tax_year_config("2025-26")
        old_slabs = config.get_slabs(TaxRegime.OLD)
        new_slabs = config.get_slabs(TaxRegime.NEW)
        assert len(old_slabs) == 4
        assert len(new_slabs) == 7
        assert old_slabs[0].rate == Decimal("0")

    def test_cess_and_surcharge_present(self) -> None:
        """Health and education cess and surcharge thresholds should exist."""
        config = get_tax_year_config("2025-26")
        assert config.health_education_cess_rate == Decimal("0.04")
        assert len(config.surcharge_thresholds) == 4

    def test_section_80_limits(self) -> None:
        """Section 80 limits should be configured."""
        config = get_tax_year_config("2025-26")
        assert config.section_80_limits.section_80c == 150_000

    def test_fifo_and_grandfathering(self) -> None:
        """FIFO and grandfathering rules should be enabled by default."""
        config = get_tax_year_config("2025-26")
        assert config.fifo.enabled is True
        assert config.grandfathering.enabled is True
