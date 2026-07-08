"""Tax assessment model unit tests."""

from decimal import Decimal

import pytest

from app.models.tax_assessment import TaxAssessment


@pytest.mark.unit
def test_tax_assessment_repr() -> None:
    """Model repr should include id, pan, and assessment year."""
    assessment = TaxAssessment(
        pan="ABCDE1234F",
        assessment_year="2025-26",
        regime="old",
        gross_total_income=Decimal("1"),
        total_deductions=Decimal("0"),
        taxable_income=Decimal("1"),
        tax_payable=Decimal("0"),
    )
    representation = repr(assessment)
    assert "ABCDE1234F" in representation
    assert "2025-26" in representation
