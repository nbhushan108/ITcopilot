"""Repository layer unit tests."""

from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tax_assessment import TaxAssessment
from app.repositories.tax_assessment_repository import TaxAssessmentRepository


@pytest.mark.integration
class TestTaxAssessmentRepository:
    """Tests for tax assessment repository."""

    async def test_create_and_get(self, db_session: AsyncSession) -> None:
        """Repository should persist and retrieve assessments."""
        repo = TaxAssessmentRepository(db_session)
        assessment = TaxAssessment(
            pan="ABCDE1234F",
            assessment_year="2025-26",
            regime="old",
            gross_total_income=Decimal("1000000"),
            total_deductions=Decimal("200000"),
            taxable_income=Decimal("800000"),
            tax_payable=Decimal("75000"),
        )
        saved = await repo.create(assessment)
        assert saved.id is not None

        fetched = await repo.get_by_id(saved.id)
        assert fetched is not None
        assert fetched.pan == "ABCDE1234F"

    async def test_list_by_pan(self, db_session: AsyncSession) -> None:
        """Repository should filter assessments by PAN."""
        repo = TaxAssessmentRepository(db_session)
        for pan in ("ABCDE1234F", "FGHIJ5678K"):
            await repo.create(
                TaxAssessment(
                    pan=pan,
                    assessment_year="2025-26",
                    regime="old",
                    gross_total_income=Decimal("500000"),
                    total_deductions=Decimal("50000"),
                    taxable_income=Decimal("450000"),
                    tax_payable=Decimal("10000"),
                ),
            )

        results = await repo.list_all(pan="ABCDE1234F")
        assert len(results) == 1
        assert results[0].pan == "ABCDE1234F"
