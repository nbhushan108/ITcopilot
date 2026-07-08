"""ITcopilot FastAPI application entry point."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from app.api.exception_handlers import create_openapi_tags, register_exception_handlers
from app.core.logging import configure_logging
from app.core.settings import Settings, get_settings
from app.db.session import init_db
from app.routers.auth import router as auth_router
from app.routers.health import router as health_router
from app.routers.tax import router as tax_router


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application startup and shutdown lifecycle events.

    Yields:
        Control to the running application.
    """
    settings = get_settings()
    configure_logging(settings)
    logger.info(
        "Starting {} v{} in {} mode",
        settings.app_name,
        settings.app_version,
        settings.environment.value,
    )

    try:
        await init_db(settings)
    except Exception as exc:
        logger.error("Database initialization failed during startup: {}", exc)
        if settings.is_production:
            raise

    logger.info("Application startup complete")
    yield
    logger.info("Application shutdown initiated")


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create and configure the FastAPI application factory.

    Args:
        settings: Optional settings override for testing.

    Returns:
        Configured FastAPI application instance.
    """
    app_settings = settings or get_settings()

    app = FastAPI(
        title=app_settings.app_name,
        description=(
            "Production-grade AI-powered Income Tax Copilot for India. "
            "Compute tax liability, manage assessments, and import broker statements."
        ),
        version=app_settings.app_version,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        openapi_tags=create_openapi_tags(),
        default_response_class=JSONResponse,
        lifespan=lifespan,
        debug=app_settings.debug,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=app_settings.cors_origins,
        allow_credentials=app_settings.cors_allow_credentials,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "Accept"],
    )

    register_exception_handlers(app)

    app.include_router(health_router, prefix=app_settings.api_prefix)
    app.include_router(auth_router, prefix=app_settings.api_prefix)
    app.include_router(tax_router, prefix=app_settings.api_prefix)

    @app.get("/", include_in_schema=False)
    async def root() -> dict[str, str]:
        """Root endpoint redirecting to API documentation."""
        return {
            "message": f"Welcome to {app_settings.app_name}",
            "docs": "/docs",
            "health": f"{app_settings.api_prefix}/health",
            "version": f"{app_settings.api_prefix}/version",
        }

    return app


app = create_app()
