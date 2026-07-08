"""API route handlers."""

from app.routers.auth import router as auth_router
from app.routers.health import router as health_router
from app.routers.tax import router as tax_router


__all__ = ["auth_router", "health_router", "tax_router"]
