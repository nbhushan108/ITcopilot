"""Common API response schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class HealthCheckDetail(BaseModel):
    """Individual health check component status."""

    status: str = Field(description="Component status: healthy or unhealthy")
    message: str = Field(default="", description="Optional detail message")


class HealthResponse(BaseModel):
    """Health check response schema."""

    status: str = Field(description="Service health status")
    timestamp: datetime = Field(description="UTC timestamp of the health check")
    environment: str = Field(description="Current deployment environment")
    version: str = Field(description="Application version")
    checks: dict[str, HealthCheckDetail] = Field(
        default_factory=dict,
        description="Component-level health checks",
    )


class VersionResponse(BaseModel):
    """Application version response schema."""

    name: str = Field(description="Application name")
    version: str = Field(description="Semantic version string")
    api_prefix: str = Field(description="API route prefix")
    environment: str = Field(description="Current deployment environment")


class MessageResponse(BaseModel):
    """Generic message response schema."""

    message: str = Field(description="Human-readable response message")


class ErrorResponse(BaseModel):
    """Standard error response schema."""

    error: str = Field(description="Error type identifier")
    message: str = Field(description="Human-readable error message")
    details: dict[str, Any] = Field(default_factory=dict, description="Additional error context")
