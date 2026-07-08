"""Pydantic request and response schemas."""

from app.schemas.common import ErrorResponse, HealthResponse, MessageResponse, VersionResponse
from app.schemas.tax import TaxAssessmentCreate, TaxAssessmentResponse, TaxComputationRequest

__all__ = [
    "ErrorResponse",
    "HealthResponse",
    "MessageResponse",
    "TaxAssessmentCreate",
    "TaxAssessmentResponse",
    "TaxComputationRequest",
    "VersionResponse",
]
