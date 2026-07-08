"""Exception handler integration tests."""

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api.exception_handlers import create_openapi_tags, register_exception_handlers
from app.core.exceptions import AuthorizationError, NotFoundError


@pytest.mark.integration
class TestExceptionHandlers:
    """Tests for global API exception handlers."""

    @pytest.fixture
    def error_app(self) -> FastAPI:
        """Provide app with routes that trigger exception handlers."""
        app = FastAPI()
        register_exception_handlers(app)

        @app.get("/not-found")
        async def not_found() -> None:
            raise NotFoundError("missing resource")

        @app.get("/forbidden")
        async def forbidden() -> None:
            raise AuthorizationError("denied")

        @app.get("/boom")
        async def boom() -> None:
            raise RuntimeError("unexpected")

        return app

    async def test_not_found_handler(self, error_app: FastAPI) -> None:
        """NotFoundError should map to HTTP 404."""
        transport = ASGITransport(app=error_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/not-found")
        assert response.status_code == 404
        assert response.json()["error"] == "NotFoundError"

    async def test_authorization_handler(self, error_app: FastAPI) -> None:
        """AuthorizationError should map to HTTP 403."""
        transport = ASGITransport(app=error_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/forbidden")
        assert response.status_code == 403

    async def test_unhandled_exception_handler(self, error_app: FastAPI) -> None:
        """Unhandled exceptions should return HTTP 500."""
        transport = ASGITransport(app=error_app, raise_app_exceptions=False)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/boom")
        assert response.status_code == 500
        assert response.json()["error"] == "InternalServerError"

    def test_create_openapi_tags(self) -> None:
        """OpenAPI tags should include core API groups."""
        tags = create_openapi_tags()
        names = {tag["name"] for tag in tags}
        assert {"Health", "Auth", "Tax"}.issubset(names)
