"""API layer utilities and exception handlers."""

from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger

from app.core.exceptions import (
    AuthenticationError,
    AuthorizationError,
    FileProcessingError,
    ITcopilotError,
    NotFoundError,
    TaxComputationError,
    ValidationError,
)
from app.schemas.common import ErrorResponse


def register_exception_handlers(app: FastAPI) -> None:
    """Register global exception handlers on the FastAPI application.

    Args:
        app: FastAPI application instance.
    """

    @app.exception_handler(ITcopilotError)
    async def itcopilot_error_handler(
        request: Request,
        exc: ITcopilotError,
    ) -> JSONResponse:
        """Handle application-specific exceptions."""
        status_code = _map_exception_to_status(exc)
        logger.warning(
            "Application error on {} {}: {}",
            request.method,
            request.url.path,
            exc.message,
        )
        return JSONResponse(
            status_code=status_code,
            content=ErrorResponse(
                error=exc.__class__.__name__,
                message=exc.message,
                details=exc.details,
            ).model_dump(),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        """Handle Pydantic/FastAPI validation errors."""
        logger.warning(
            "Validation error on {} {}: {}",
            request.method,
            request.url.path,
            exc.errors(),
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content=ErrorResponse(
                error="ValidationError",
                message="Request validation failed",
                details={"errors": exc.errors()},
            ).model_dump(),
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        """Handle unexpected exceptions."""
        logger.exception(
            "Unhandled error on {} {}: {}",
            request.method,
            request.url.path,
            exc,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                error="InternalServerError",
                message="An unexpected error occurred",
            ).model_dump(),
        )


def _map_exception_to_status(exc: ITcopilotError) -> int:
    """Map exception type to HTTP status code.

    Args:
        exc: Application exception instance.

    Returns:
        HTTP status code integer.
    """
    mapping: dict[type[ITcopilotError], int] = {
        NotFoundError: status.HTTP_404_NOT_FOUND,
        ValidationError: status.HTTP_422_UNPROCESSABLE_CONTENT,
        AuthenticationError: status.HTTP_401_UNAUTHORIZED,
        AuthorizationError: status.HTTP_403_FORBIDDEN,
        FileProcessingError: status.HTTP_422_UNPROCESSABLE_CONTENT,
        TaxComputationError: status.HTTP_422_UNPROCESSABLE_CONTENT,
    }
    return mapping.get(type(exc), status.HTTP_400_BAD_REQUEST)


def create_openapi_tags() -> list[dict[str, Any]]:
    """Return OpenAPI tag metadata for API documentation.

    Returns:
        List of tag definition dictionaries.
    """
    return [
        {
            "name": "Health",
            "description": "Service health and version endpoints",
        },
        {
            "name": "Auth",
            "description": "Authentication and token management",
        },
        {
            "name": "Tax",
            "description": "Income tax computation and assessment management",
        },
    ]
