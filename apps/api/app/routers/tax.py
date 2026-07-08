"""Tax computation and assessment API routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, require_authenticated_user
from app.repositories.tax_assessment_repository import TaxAssessmentRepository
from app.schemas.auth import CurrentUser
from app.schemas.tax import TaxAssessmentResponse, TaxComputationRequest
from app.services.tax_service import TaxService

router = APIRouter(prefix="/tax", tags=["Tax"])


def get_tax_repository(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> TaxAssessmentRepository:
    """Provide TaxAssessmentRepository via dependency injection."""
    return TaxAssessmentRepository(session=session)


def get_tax_service(
    repository: Annotated[TaxAssessmentRepository, Depends(get_tax_repository)],
) -> TaxService:
    """Provide TaxService via dependency injection."""
    return TaxService(repository=repository)


@router.post(
    "/compute",
    response_model=TaxAssessmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Compute income tax",
    description="Compute income tax liability based on income and deductions.",
)
async def compute_tax(
    request: TaxComputationRequest,
    service: Annotated[TaxService, Depends(get_tax_service)],
    _user: Annotated[CurrentUser, Depends(require_authenticated_user)],
) -> TaxAssessmentResponse:
    """Compute and persist tax assessment."""
    return await service.compute_tax(request)


@router.get(
    "/assessments/{assessment_id}",
    response_model=TaxAssessmentResponse,
    summary="Get tax assessment",
    description="Retrieve a tax assessment by its unique identifier.",
)
async def get_assessment(
    assessment_id: str,
    service: Annotated[TaxService, Depends(get_tax_service)],
    _user: Annotated[CurrentUser, Depends(require_authenticated_user)],
) -> TaxAssessmentResponse:
    """Retrieve a single tax assessment."""
    return await service.get_assessment(assessment_id)


@router.get(
    "/assessments",
    response_model=list[TaxAssessmentResponse],
    summary="List tax assessments",
    description="List tax assessments with optional PAN filter and pagination.",
)
async def list_assessments(
    service: Annotated[TaxService, Depends(get_tax_service)],
    _user: Annotated[CurrentUser, Depends(require_authenticated_user)],
    pan: str | None = Query(default=None, min_length=10, max_length=10),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> list[TaxAssessmentResponse]:
    """List tax assessments."""
    return await service.list_assessments(pan=pan, limit=limit, offset=offset)
