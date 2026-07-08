"""Tax service unit tests."""

from decimal import Decimal
from unittest.mock import AsyncMock, patch

import pytest

from app.core.exceptions import NotFoundError, TaxComputationError, ValidationError
from app.models.tax_assessment import TaxAssessment
from app.repositories.tax_assessment_repository import TaxAssessmentRepository
from app.schemas.tax import TaxAssessmentCreate, TaxComputationRequest
from app.services.tax_service import TaxService


@pytest.mark.unit
class TestTaxService:
    """Tests for tax computation service."""

    @pytest.fixture
    def repository(self) -> AsyncMock:
        """Provide mocked repository."""
        return AsyncMock(spec=TaxAssessmentRepository)

    @pytest.fixture
    def service(self, repository: AsyncMock) -> TaxService:
        """Provide tax service with mocked repository."""
        return TaxService(repository=repository)

    @pytest.mark.asyncio
    async def test_get_assessment_not_found(
        self,
        service: TaxService,
        repository: AsyncMock,
    ) -> None:
        """Missing assessments should raise NotFoundError."""
        repository.get_by_id.return_value = None
        with pytest.raises(NotFoundError):
            await service.get_assessment("missing-id")

    @pytest.mark.asyncio
    async def test_compute_tax_validation_error(self, service: TaxService) -> None:
        """Calculator ValueError should map to ValidationError."""
        request = TaxComputationRequest(
            pan="ABCDE1234F",
            assessment_year="2025-26",
            gross_salary=Decimal("100000"),
        )
        with patch.object(service._calculator, "compute", side_effect=ValueError("bad input")):
            with pytest.raises(ValidationError, match="bad input"):
                await service.compute_tax(request)

    @pytest.mark.asyncio
    async def test_compute_tax_unexpected_error(self, service: TaxService) -> None:
        """Unexpected calculator failures should raise TaxComputationError."""
        request = TaxComputationRequest(
            pan="ABCDE1234F",
            assessment_year="2025-26",
            gross_salary=Decimal("100000"),
        )
        with patch.object(service._calculator, "compute", side_effect=RuntimeError("boom")):
            with pytest.raises(TaxComputationError):
                await service.compute_tax(request)

    @pytest.mark.asyncio
    async def test_get_total_tax_collected(self, service: TaxService) -> None:
        """Total tax should sum payable amounts for a PAN."""
        from datetime import UTC, datetime

        from app.schemas.tax import TaxAssessmentResponse

        assessments = [
            TaxAssessmentResponse(
                id="1",
                pan="ABCDE1234F",
                assessment_year="2025-26",
                regime="old",
                gross_total_income=Decimal("100"),
                total_deductions=Decimal("0"),
                taxable_income=Decimal("100"),
                tax_payable=Decimal("10"),
                notes=None,
                created_at=datetime.now(tz=UTC),
                updated_at=datetime.now(tz=UTC),
            ),
            TaxAssessmentResponse(
                id="2",
                pan="ABCDE1234F",
                assessment_year="2025-26",
                regime="old",
                gross_total_income=Decimal("200"),
                total_deductions=Decimal("0"),
                taxable_income=Decimal("200"),
                tax_payable=Decimal("20"),
                notes=None,
                created_at=datetime.now(tz=UTC),
                updated_at=datetime.now(tz=UTC),
            ),
        ]
        with patch.object(service, "list_assessments", return_value=assessments):
            total = await service.get_total_tax_collected("ABCDE1234F")
        assert total == Decimal("30")

    @pytest.mark.asyncio
    async def test_create_assessment_persists(
        self,
        service: TaxService,
        repository: AsyncMock,
    ) -> None:
        """create_assessment should delegate to repository."""
        from datetime import UTC, datetime

        now = datetime.now(tz=UTC)
        saved = TaxAssessment(
            id="saved-id",
            pan="ABCDE1234F",
            assessment_year="2025-26",
            regime="old",
            gross_total_income=Decimal("1"),
            total_deductions=Decimal("0"),
            taxable_income=Decimal("1"),
            tax_payable=Decimal("0"),
        )
        saved.created_at = now
        saved.updated_at = now
        repository.create.return_value = saved

        data = TaxAssessmentCreate(
            pan="ABCDE1234F",
            assessment_year="2025-26",
            regime="old",
            gross_total_income=Decimal("1"),
            total_deductions=Decimal("0"),
            taxable_income=Decimal("1"),
            tax_payable=Decimal("0"),
        )
        result = await service.create_assessment(data)
        repository.create.assert_awaited_once()
        assert result.pan == "ABCDE1234F"
