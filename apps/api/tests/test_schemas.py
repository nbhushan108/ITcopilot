"""Tax schema validation unit tests."""

import pytest
from pydantic import ValidationError as PydanticValidationError

from app.schemas.tax import TaxAssessmentCreate, TaxComputationRequest


@pytest.mark.unit
class TestTaxSchemas:
    """Tests for tax-related pydantic schemas."""

    def test_tax_computation_request_invalid_pan(self) -> None:
        """TaxComputationRequest should reject invalid PAN values."""
        with pytest.raises(PydanticValidationError):
            TaxComputationRequest(pan="BADPAN", assessment_year="2025-26")

    def test_tax_assessment_create_invalid_pan(self) -> None:
        """TaxAssessmentCreate should reject invalid PAN values."""
        from decimal import Decimal

        with pytest.raises(PydanticValidationError):
            TaxAssessmentCreate(
                pan="BADPAN",
                assessment_year="2025-26",
                regime="old",
                gross_total_income=Decimal("1"),
                total_deductions=Decimal("0"),
                taxable_income=Decimal("1"),
                tax_payable=Decimal("0"),
            )
