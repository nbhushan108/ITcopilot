"""Tax computation and assessment service."""

from decimal import Decimal

from loguru import logger

from app.core.exceptions import NotFoundError, TaxComputationError, ValidationError
from app.models.tax_assessment import TaxAssessment
from app.repositories.tax_assessment_repository import TaxAssessmentRepository
from app.schemas.tax import TaxAssessmentCreate, TaxAssessmentResponse, TaxComputationRequest
from tax_engine.calculator import TaxCalculator
from tax_engine.models import IncomeBreakdown, TaxRegime


class TaxService:
    """Service for tax computation and assessment management."""

    def __init__(self, repository: TaxAssessmentRepository) -> None:
        """Initialize tax service with repository.

        Args:
            repository: Tax assessment data access layer.
        """
        self._repository = repository
        self._logger = logger.bind(service="TaxService")
        self._calculator = TaxCalculator()

    async def compute_tax(self, request: TaxComputationRequest) -> TaxAssessmentResponse:
        """Compute tax liability and persist the assessment.

        Args:
            request: Tax computation input parameters.

        Returns:
            TaxAssessmentResponse with computed tax details.

        Raises:
            TaxComputationError: If tax calculation fails.
            ValidationError: If input validation fails at service layer.
        """
        self._logger.info(
            "Computing tax for PAN={} AY={} regime={}",
            request.pan[:4] + "****",
            request.assessment_year,
            request.regime,
        )

        try:
            regime = TaxRegime.NEW if request.regime == "new" else TaxRegime.OLD
            income = IncomeBreakdown(
                gross_salary=request.gross_salary,
                other_income=request.other_income,
                section_80c=request.section_80c,
                section_80d=request.section_80d,
                hra_exemption=request.hra_exemption,
                standard_deduction=request.standard_deduction,
            )
            result = self._calculator.compute(
                income=income,
                regime=regime,
                assessment_year=request.assessment_year,
            )
        except ValueError as exc:
            self._logger.warning("Tax computation validation failed: {}", exc)
            raise ValidationError(str(exc)) from exc
        except Exception as exc:
            self._logger.error("Tax computation failed: {}", exc)
            raise TaxComputationError("Failed to compute tax liability") from exc

        assessment_data = TaxAssessmentCreate(
            pan=request.pan,
            assessment_year=request.assessment_year,
            regime=request.regime,
            gross_total_income=result.gross_total_income,
            total_deductions=result.total_deductions,
            taxable_income=result.taxable_income,
            tax_payable=result.total_tax_payable,
            notes=f"Computed via {request.regime} regime for AY {request.assessment_year}",
        )

        return await self.create_assessment(assessment_data)

    async def create_assessment(self, data: TaxAssessmentCreate) -> TaxAssessmentResponse:
        """Create and persist a new tax assessment record.

        Args:
            data: Tax assessment creation payload.

        Returns:
            Created TaxAssessmentResponse.
        """
        assessment = TaxAssessment(
            pan=data.pan,
            assessment_year=data.assessment_year,
            regime=data.regime,
            gross_total_income=data.gross_total_income,
            total_deductions=data.total_deductions,
            taxable_income=data.taxable_income,
            tax_payable=data.tax_payable,
            notes=data.notes,
        )
        saved = await self._repository.create(assessment)
        self._logger.info("Created tax assessment id={}", saved.id)
        return TaxAssessmentResponse.model_validate(saved)

    async def get_assessment(self, assessment_id: str) -> TaxAssessmentResponse:
        """Retrieve a tax assessment by ID.

        Args:
            assessment_id: UUID of the tax assessment.

        Returns:
            TaxAssessmentResponse for the requested assessment.

        Raises:
            NotFoundError: If assessment does not exist.
        """
        assessment = await self._repository.get_by_id(assessment_id)

        if assessment is None:
            self._logger.warning("Tax assessment not found: id={}", assessment_id)
            raise NotFoundError(f"Tax assessment not found: {assessment_id}")

        return TaxAssessmentResponse.model_validate(assessment)

    async def list_assessments(
        self,
        pan: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[TaxAssessmentResponse]:
        """List tax assessments with optional PAN filter.

        Args:
            pan: Optional PAN to filter assessments.
            limit: Maximum number of records to return.
            offset: Number of records to skip.

        Returns:
            List of TaxAssessmentResponse objects.
        """
        assessments = await self._repository.list_all(pan=pan, limit=limit, offset=offset)
        return [TaxAssessmentResponse.model_validate(a) for a in assessments]

    async def get_total_tax_collected(self, pan: str) -> Decimal:
        """Calculate total tax payable across all assessments for a PAN.

        Args:
            pan: Permanent Account Number.

        Returns:
            Sum of tax payable across all assessments.
        """
        assessments = await self.list_assessments(pan=pan, limit=1000)
        return sum((a.tax_payable for a in assessments), Decimal("0"))
