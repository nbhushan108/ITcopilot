"""Tax engine unit tests."""

from decimal import Decimal

import pytest

from tax_engine.calculator import TaxCalculator
from tax_engine.models import IncomeBreakdown, TaxRegime


@pytest.mark.unit
class TestTaxCalculator:
    """Unit tests for TaxCalculator."""

    @pytest.fixture
    def calculator(self) -> TaxCalculator:
        """Provide TaxCalculator instance."""
        return TaxCalculator()

    def test_old_regime_basic_computation(self, calculator: TaxCalculator) -> None:
        """Old regime should compute tax with deductions."""
        income = IncomeBreakdown(
            gross_salary=Decimal("1000000"),
            section_80c=Decimal("150000"),
            standard_deduction=Decimal("50000"),
        )
        result = calculator.compute(
            income=income,
            regime=TaxRegime.OLD,
            assessment_year="2025-26",
        )

        assert result.gross_total_income == Decimal("1000000")
        assert result.total_deductions == Decimal("200000")
        assert result.taxable_income == Decimal("800000")
        assert result.total_tax_payable > 0

    def test_new_regime_no_deductions(self, calculator: TaxCalculator) -> None:
        """New regime should only apply standard deduction."""
        income = IncomeBreakdown(
            gross_salary=Decimal("1000000"),
            section_80c=Decimal("150000"),
            standard_deduction=Decimal("75000"),
        )
        result = calculator.compute(
            income=income,
            regime=TaxRegime.NEW,
            assessment_year="2025-26",
        )

        assert result.total_deductions == Decimal("75000")
        assert result.taxable_income == Decimal("925000")

    def test_zero_income_zero_tax(self, calculator: TaxCalculator) -> None:
        """Zero income should result in zero tax."""
        income = IncomeBreakdown()
        result = calculator.compute(
            income=income,
            regime=TaxRegime.OLD,
            assessment_year="2025-26",
        )

        assert result.total_tax_payable == Decimal("0")
        assert result.effective_tax_rate == Decimal("0")

    def test_negative_income_raises(self, calculator: TaxCalculator) -> None:
        """Negative gross income should raise ValueError."""
        income = IncomeBreakdown.model_construct(gross_salary=Decimal("-100"))
        with pytest.raises(ValueError, match="cannot be negative"):
            calculator.compute(
                income=income,
                regime=TaxRegime.OLD,
                assessment_year="2025-26",
            )

    def test_surcharge_for_high_income(self, calculator: TaxCalculator) -> None:
        """High income should attract surcharge."""
        income = IncomeBreakdown(
            gross_salary=Decimal("6000000"),
            standard_deduction=Decimal("50000"),
        )
        result = calculator.compute(
            income=income,
            regime=TaxRegime.OLD,
            assessment_year="2025-26",
        )

        assert result.surcharge > 0
        assert result.cess > 0
