"""Tax configuration definitions for multiple assessment years."""

from datetime import date
from decimal import Decimal
from functools import lru_cache

from pydantic import BaseModel, Field

from common.config.exceptions import ConfigurationError
from common.config.types import ResidentStatus, TaxRegime, TaxSlabDefinition
from common.config.validators import validate_assessment_year


class Section80Limits(BaseModel):
    """Chapter VI-A deduction limits for a given assessment year."""

    section_80c: int = Field(default=150_000)
    section_80d_self: int = Field(default=25_000)
    section_80d_parents: int = Field(default=50_000)
    section_80ccd_1b: int = Field(default=50_000)
    section_80g: int = Field(default=0, description="Qualifying limit varies by donee")

    model_config = {"frozen": True}


class CapitalGainRates(BaseModel):
    """Capital gains tax rate configuration."""

    stcg_equity: Decimal = Field(default=Decimal("0.15"))
    ltcg_equity: Decimal = Field(default=Decimal("0.10"))
    stcg_debt: Decimal = Field(default=Decimal("0.30"))
    ltcg_debt: Decimal = Field(default=Decimal("0.20"))
    ltcg_exemption_limit: Decimal = Field(default=Decimal("100000"))

    model_config = {"frozen": True}


class FifoConfiguration(BaseModel):
    """First-In-First-Out matching configuration for capital gains."""

    enabled: bool = Field(default=True)
    match_across_fy: bool = Field(default=False)
    include_corporate_actions: bool = Field(default=True)

    model_config = {"frozen": True}


class GrandfatheringRules(BaseModel):
    """LTCG grandfathering rules for equity investments."""

    enabled: bool = Field(default=True)
    cutoff_date: date = Field(default=date(2018, 1, 31))
    use_highest_price_before_cutoff: bool = Field(default=True)

    model_config = {"frozen": True}


class TaxYearConfiguration(BaseModel):
    """Complete tax configuration for one assessment year."""

    financial_year: str
    assessment_year: str
    resident_status: ResidentStatus = ResidentStatus.RESIDENT
    default_regime: TaxRegime = TaxRegime.OLD
    old_regime_slabs: tuple[TaxSlabDefinition, ...]
    new_regime_slabs: tuple[TaxSlabDefinition, ...]
    health_education_cess_rate: Decimal = Field(default=Decimal("0.04"))
    surcharge_thresholds: tuple[tuple[Decimal, Decimal], ...]
    section_80_limits: Section80Limits = Field(default_factory=Section80Limits)
    capital_gain_rates: CapitalGainRates = Field(default_factory=CapitalGainRates)
    fifo: FifoConfiguration = Field(default_factory=FifoConfiguration)
    grandfathering: GrandfatheringRules = Field(default_factory=GrandfatheringRules)
    standard_deduction_old: int = Field(default=50_000)
    standard_deduction_new: int = Field(default=75_000)

    model_config = {"frozen": True}

    def get_slabs(self, regime: TaxRegime) -> tuple[TaxSlabDefinition, ...]:
        """Return tax slabs for the requested regime.

        Args:
            regime: Old or new tax regime.

        Returns:
            Progressive slab definitions for the regime.
        """
        if regime == TaxRegime.NEW:
            return self.new_regime_slabs
        return self.old_regime_slabs


def _build_default_tax_configs() -> dict[str, TaxYearConfiguration]:
    """Build built-in tax year configurations."""
    old_slabs = (
        TaxSlabDefinition(lower=Decimal("0"), upper=Decimal("250000"), rate=Decimal("0")),
        TaxSlabDefinition(lower=Decimal("250000"), upper=Decimal("500000"), rate=Decimal("0.05")),
        TaxSlabDefinition(lower=Decimal("500000"), upper=Decimal("1000000"), rate=Decimal("0.20")),
        TaxSlabDefinition(lower=Decimal("1000000"), upper=None, rate=Decimal("0.30")),
    )
    new_slabs = (
        TaxSlabDefinition(lower=Decimal("0"), upper=Decimal("400000"), rate=Decimal("0")),
        TaxSlabDefinition(lower=Decimal("400000"), upper=Decimal("800000"), rate=Decimal("0.05")),
        TaxSlabDefinition(lower=Decimal("800000"), upper=Decimal("1200000"), rate=Decimal("0.10")),
        TaxSlabDefinition(lower=Decimal("1200000"), upper=Decimal("1600000"), rate=Decimal("0.15")),
        TaxSlabDefinition(lower=Decimal("1600000"), upper=Decimal("2000000"), rate=Decimal("0.20")),
        TaxSlabDefinition(lower=Decimal("2000000"), upper=Decimal("2400000"), rate=Decimal("0.25")),
        TaxSlabDefinition(lower=Decimal("2400000"), upper=None, rate=Decimal("0.30")),
    )
    surcharge = (
        (Decimal("5000000"), Decimal("0.10")),
        (Decimal("10000000"), Decimal("0.15")),
        (Decimal("20000000"), Decimal("0.25")),
        (Decimal("50000000"), Decimal("0.37")),
    )

    configs: dict[str, TaxYearConfiguration] = {}
    for assessment_year, financial_year in (
        ("2023-24", "2022-23"),
        ("2024-25", "2023-24"),
        ("2025-26", "2024-25"),
    ):
        configs[assessment_year] = TaxYearConfiguration(
            financial_year=financial_year,
            assessment_year=assessment_year,
            old_regime_slabs=old_slabs,
            new_regime_slabs=new_slabs,
            surcharge_thresholds=surcharge,
        )
    return configs


TAX_YEAR_CONFIGURATIONS: dict[str, TaxYearConfiguration] = _build_default_tax_configs()


def get_tax_year_config(assessment_year: str) -> TaxYearConfiguration:
    """Return tax configuration for an assessment year.

    Args:
        assessment_year: Assessment year in ``YYYY-YY`` format.

    Returns:
        Tax configuration for the requested year.

    Raises:
        ConfigurationError: If the assessment year is invalid or unsupported.
    """
    validated = validate_assessment_year(assessment_year)
    config = TAX_YEAR_CONFIGURATIONS.get(validated)
    if config is None:
        supported = ", ".join(sorted(TAX_YEAR_CONFIGURATIONS))
        raise ConfigurationError(
            f"No tax configuration registered for {validated!r}. Supported: {supported}",
        )
    return config


@lru_cache
def get_default_tax_config() -> TaxYearConfiguration:
    """Return the default tax configuration for the latest supported year."""
    latest = max(TAX_YEAR_CONFIGURATIONS)
    return TAX_YEAR_CONFIGURATIONS[latest]
