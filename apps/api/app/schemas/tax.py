"""Tax-related Pydantic schemas."""

import re
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


PAN_PATTERN = re.compile(r"^[A-Z]{5}[0-9]{4}[A-Z]$")


class TaxComputationRequest(BaseModel):
    """Request schema for tax computation."""

    pan: str = Field(description="Permanent Account Number", min_length=10, max_length=10)
    assessment_year: str = Field(
        description="Assessment year e.g. 2025-26", pattern=r"^\d{4}-\d{2}$"
    )
    regime: str = Field(default="old", pattern=r"^(old|new)$")
    gross_salary: Decimal = Field(default=Decimal("0"), ge=0)
    other_income: Decimal = Field(default=Decimal("0"), ge=0)
    section_80c: Decimal = Field(default=Decimal("0"), ge=0, le=150000)
    section_80d: Decimal = Field(default=Decimal("0"), ge=0)
    hra_exemption: Decimal = Field(default=Decimal("0"), ge=0)
    standard_deduction: Decimal = Field(default=Decimal("75000"), ge=0)

    @field_validator("pan")
    @classmethod
    def validate_pan(cls, value: str) -> str:
        """Validate PAN format."""
        normalized = value.upper().strip()
        if not PAN_PATTERN.match(normalized):
            raise ValueError("Invalid PAN format. Expected format: ABCDE1234F")
        return normalized


class TaxAssessmentCreate(BaseModel):
    """Schema for creating a tax assessment record."""

    pan: str = Field(min_length=10, max_length=10)
    assessment_year: str = Field(pattern=r"^\d{4}-\d{2}$")
    regime: str = Field(default="old", pattern=r"^(old|new)$")
    gross_total_income: Decimal = Field(ge=0)
    total_deductions: Decimal = Field(ge=0)
    taxable_income: Decimal = Field(ge=0)
    tax_payable: Decimal = Field(ge=0)
    notes: str | None = None

    @field_validator("pan")
    @classmethod
    def validate_pan(cls, value: str) -> str:
        """Validate PAN format."""
        normalized = value.upper().strip()
        if not PAN_PATTERN.match(normalized):
            raise ValueError("Invalid PAN format. Expected format: ABCDE1234F")
        return normalized


class TaxAssessmentResponse(BaseModel):
    """Response schema for tax assessment records."""

    id: str
    pan: str
    assessment_year: str
    regime: str
    gross_total_income: Decimal
    total_deductions: Decimal
    taxable_income: Decimal
    tax_payable: Decimal
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
