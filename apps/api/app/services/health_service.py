"""Health check service."""

from datetime import UTC, datetime

from loguru import logger

from app.core.settings import Settings
from app.db.session import check_database_connectivity
from app.schemas.common import HealthCheckDetail, HealthResponse, VersionResponse


class HealthService:
    """Service for application health and version endpoints."""

    def __init__(self, settings: Settings) -> None:
        """Initialize health service with application settings.

        Args:
            settings: Application configuration settings.
        """
        self._settings = settings
        self._logger = logger.bind(service="HealthService")

    async def get_liveness(self) -> HealthResponse:
        """Return liveness status (process is running).

        Returns:
            HealthResponse indicating the process is alive.
        """
        self._logger.debug("Liveness check requested")
        return HealthResponse(
            status="healthy",
            timestamp=datetime.now(tz=UTC),
            environment=self._settings.environment.value,
            version=self._settings.app_version,
            checks={"process": HealthCheckDetail(status="healthy", message="Process running")},
        )

    async def get_readiness(self) -> HealthResponse:
        """Return readiness status including dependency checks.

        Returns:
            HealthResponse with database connectivity check.
        """
        self._logger.debug("Readiness check requested")
        db_healthy = await check_database_connectivity()
        checks = {
            "database": HealthCheckDetail(
                status="healthy" if db_healthy else "unhealthy",
                message="Connected" if db_healthy else "Database unreachable",
            ),
        }
        overall = "healthy" if db_healthy else "unhealthy"
        return HealthResponse(
            status=overall,
            timestamp=datetime.now(tz=UTC),
            environment=self._settings.environment.value,
            version=self._settings.app_version,
            checks=checks,
        )

    async def get_health(self) -> HealthResponse:
        """Return combined health status (alias for readiness).

        Returns:
            HealthResponse with dependency checks.
        """
        return await self.get_readiness()

    def get_version(self) -> VersionResponse:
        """Return application version information.

        Returns:
            VersionResponse with name, version, API prefix, and environment.
        """
        self._logger.debug("Version check requested")
        return VersionResponse(
            name=self._settings.app_name,
            version=self._settings.app_version,
            api_prefix=self._settings.api_prefix,
            environment=self._settings.environment.value,
        )
