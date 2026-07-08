"""Report data models."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from tax_engine.models import TaxComputationResult


class TaxReportSection(BaseModel):
    """A section within a tax report."""

    title: str
    rows: list[dict[str, str | Decimal | int | float]] = Field(default_factory=list)
    subtotal: Decimal | None = None


class TaxReport(BaseModel):
    """Complete tax report document."""

    title: str
    pan: str
    assessment_year: str
    generated_at: datetime = Field(default_factory=datetime.now)
    computation: TaxComputationResult
    sections: list[TaxReportSection] = Field(default_factory=list)
    summary: dict[str, str | Decimal] = Field(default_factory=dict)
