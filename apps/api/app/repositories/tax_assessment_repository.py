"""Tax assessment repository for database persistence."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tax_assessment import TaxAssessment


class TaxAssessmentRepository:
    """Repository for tax assessment CRUD operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session.

        Args:
            session: Async SQLAlchemy session.
        """
        self._session = session

    async def create(self, assessment: TaxAssessment) -> TaxAssessment:
        """Persist a new tax assessment.

        Args:
            assessment: ORM model instance to persist.

        Returns:
            Persisted assessment with refreshed fields.
        """
        self._session.add(assessment)
        await self._session.flush()
        await self._session.refresh(assessment)
        return assessment

    async def get_by_id(self, assessment_id: str) -> TaxAssessment | None:
        """Retrieve assessment by primary key.

        Args:
            assessment_id: UUID of the assessment.

        Returns:
            TaxAssessment or None if not found.
        """
        result = await self._session.execute(
            select(TaxAssessment).where(TaxAssessment.id == assessment_id),
        )
        return result.scalar_one_or_none()

    async def list_all(
        self,
        pan: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[TaxAssessment]:
        """List assessments with optional PAN filter.

        Args:
            pan: Optional PAN filter.
            limit: Maximum records to return.
            offset: Pagination offset.

        Returns:
            List of TaxAssessment records.
        """
        query = select(TaxAssessment).order_by(TaxAssessment.created_at.desc())
        if pan:
            query = query.where(TaxAssessment.pan == pan.upper())
        query = query.limit(limit).offset(offset)
        result = await self._session.execute(query)
        return list(result.scalars().all())
