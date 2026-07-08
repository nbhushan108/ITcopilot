"""Health and version API routes."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.dependencies import get_settings_dependency
from app.core.settings import Settings
from app.schemas.common import HealthResponse, VersionResponse
from app.services.health_service import HealthService


router = APIRouter(tags=["Health"])


def get_health_service(
    settings: Annotated[Settings, Depends(get_settings_dependency)],
) -> HealthService:
    """Provide HealthService via dependency injection."""
    return HealthService(settings=settings)


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check (readiness)",
    description="Returns readiness status including database connectivity.",
)
async def health_check(
    service: Annotated[HealthService, Depends(get_health_service)],
) -> HealthResponse:
    """Return application readiness status."""
    return await service.get_readiness()


@router.get(
    "/health/live",
    response_model=HealthResponse,
    summary="Liveness probe",
    description="Returns whether the application process is running.",
)
async def liveness_check(
    service: Annotated[HealthService, Depends(get_health_service)],
) -> HealthResponse:
    """Return application liveness status."""
    return await service.get_liveness()


@router.get(
    "/health/ready",
    response_model=HealthResponse,
    summary="Readiness probe",
    description="Returns whether the application can serve traffic.",
)
async def readiness_check(
    service: Annotated[HealthService, Depends(get_health_service)],
) -> HealthResponse:
    """Return application readiness status."""
    return await service.get_readiness()


@router.get(
    "/version",
    response_model=VersionResponse,
    summary="Version information",
    description="Returns application name, version, and environment details.",
)
async def version_info(
    service: Annotated[HealthService, Depends(get_health_service)],
) -> VersionResponse:
    """Return application version information."""
    return service.get_version()
