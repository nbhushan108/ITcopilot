"""FastAPI dependency injection providers."""

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthenticationError
from app.core.security import decode_access_token
from app.core.settings import Settings, get_settings
from app.db.session import get_db_session
from app.schemas.auth import CurrentUser


_bearer_scheme = HTTPBearer(auto_error=False)


async def get_settings_dependency() -> Settings:
    """Provide application settings via dependency injection."""
    return get_settings()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Provide database session via dependency injection."""
    async for session in get_db_session():
        yield session


async def get_current_user(
    settings: Annotated[Settings, Depends(get_settings_dependency)],
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(_bearer_scheme),
    ] = None,
) -> CurrentUser:
    """Resolve the authenticated user from a Bearer JWT token.

    When auth is disabled (development/testing), returns a default user.

    Args:
        settings: Application settings.
        credentials: Optional Bearer token credentials.

    Returns:
        CurrentUser context.

    Raises:
        AuthenticationError: If auth is enabled and token is missing or invalid.
    """
    if not settings.auth_enabled:
        return CurrentUser(username=settings.auth_default_username)

    if credentials is None or not credentials.credentials:
        raise AuthenticationError("Authentication required")

    username = decode_access_token(credentials.credentials, settings)
    return CurrentUser(username=username)


async def require_authenticated_user(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
) -> CurrentUser:
    """Require an authenticated user for protected endpoints.

    Args:
        current_user: Resolved user from JWT or dev bypass.

    Returns:
        Authenticated CurrentUser.
    """
    return current_user
