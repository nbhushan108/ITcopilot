"""Income tax calculator for Indian tax regimes."""

from decimal import Decimal

from loguru import logger

from common.constants import SECTION_80C_LIMIT
from tax_engine.models import IncomeBreakdown, TaxComputationResult, TaxRegime
from tax_engine.slabs import (
    CESS_RATE,
    NEW_REGIME_SLABS,
    OLD_REGIME_SLABS,
    compute_slab_tax,
    compute_surcharge,
)


class TaxCalculator:
    """Calculator for Indian income tax under old and new regimes."""

    def compute(
        self,
        income: IncomeBreakdown,
        regime: TaxRegime,
        assessment_year: str,
    ) -> TaxComputationResult:
        """Compute complete tax liability for given income and regime.

        Args:
            income: Income and deduction breakdown.
            regime: Tax regime (old or new).
            assessment_year: Assessment year e.g. '2025-26'.

        Returns:
            Complete TaxComputationResult with slab breakdown.

        Raises:
            ValueError: If assessment year or income values are invalid.
        """
        if income.gross_total_income < 0:
            raise ValueError("Gross total income cannot be negative")

        logger.info(
            "Computing tax: regime={} ay={} gti={}",
            regime.value,
            assessment_year,
            income.gross_total_income,
        )

        total_deductions = self._calculate_deductions(income, regime)
        taxable_income = max(income.gross_total_income - total_deductions, Decimal("0"))

        slabs = NEW_REGIME_SLABS if regime == TaxRegime.NEW else OLD_REGIME_SLABS
        base_tax, slab_breakdown = compute_slab_tax(taxable_income, slabs)
        surcharge = compute_surcharge(taxable_income, base_tax)
        cess = ((base_tax + surcharge) * CESS_RATE).quantize(Decimal("0.01"))
        total_tax = base_tax + surcharge + cess

        effective_rate = (
            (total_tax / income.gross_total_income * 100).quantize(Decimal("0.01"))
            if income.gross_total_income > 0
            else Decimal("0")
        )

        result = TaxComputationResult(
            regime=regime,
            assessment_year=assessment_year,
            gross_total_income=income.gross_total_income,
            total_deductions=total_deductions,
            taxable_income=taxable_income,
            base_tax=base_tax,
            surcharge=surcharge,
            cess=cess,
            total_tax_payable=total_tax,
            effective_tax_rate=effective_rate,
            slab_breakdown=slab_breakdown,
        )

        logger.info(
            "Tax computed: taxable={} tax={} effective_rate={}%",
            taxable_income,
            total_tax,
            effective_rate,
        )
        return result

    def _calculate_deductions(
        self,
        income: IncomeBreakdown,
        regime: TaxRegime,
    ) -> Decimal:
        """Calculate total deductions based on regime.

        Args:
            income: Income breakdown with deduction components.
            regime: Applicable tax regime.

        Returns:
            Total deduction amount.
        """
        standard = income.standard_deduction

        if regime == TaxRegime.NEW:
            return standard

        section_80c = min(income.section_80c, Decimal(str(SECTION_80C_LIMIT)))
        return (
            standard
            + section_80c
            + income.section_80d
            + income.hra_exemption
            + income.professional_tax
            + income.other_deductions
        )
