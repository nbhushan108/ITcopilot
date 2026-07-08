"""Tax engine domain models."""

from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, Field


class TaxRegime(StrEnum):
    """Supported income tax regimes in India."""

    OLD = "old"
    NEW = "new"


class IncomeBreakdown(BaseModel):
    """Breakdown of income and deductions for tax computation."""

    gross_salary: Decimal = Field(default=Decimal("0"), ge=0)
    other_income: Decimal = Field(default=Decimal("0"), ge=0)
    section_80c: Decimal = Field(default=Decimal("0"), ge=0, le=150000)
    section_80d: Decimal = Field(default=Decimal("0"), ge=0)
    hra_exemption: Decimal = Field(default=Decimal("0"), ge=0)
    standard_deduction: Decimal = Field(default=Decimal("75000"), ge=0)
    professional_tax: Decimal = Field(default=Decimal("0"), ge=0)
    other_deductions: Decimal = Field(default=Decimal("0"), ge=0)

    @property
    def gross_total_income(self) -> Decimal:
        """Calculate gross total income."""
        return self.gross_salary + self.other_income


class TaxSlabBreakdown(BaseModel):
    """Tax computed for a single slab."""

    lower_limit: Decimal
    upper_limit: Decimal | None
    rate: Decimal
    taxable_amount: Decimal
    tax_amount: Decimal


class TaxComputationResult(BaseModel):
    """Complete result of a tax computation."""

    regime: TaxRegime
    assessment_year: str
    gross_total_income: Decimal
    total_deductions: Decimal
    taxable_income: Decimal
    base_tax: Decimal
    surcharge: Decimal
    cess: Decimal
    total_tax_payable: Decimal
    effective_tax_rate: Decimal
    slab_breakdown: list[TaxSlabBreakdown] = Field(default_factory=list)
