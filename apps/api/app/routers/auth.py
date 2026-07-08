"""Authentication API routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.core.dependencies import get_settings_dependency
from app.core.exceptions import AuthenticationError
from app.core.security import create_access_token, verify_password
from app.core.settings import Settings
from app.schemas.auth import TokenRequest, TokenResponse


router = APIRouter(prefix="/auth", tags=["Auth"])


def _verify_admin_credentials(password: str, settings: Settings) -> bool:
    """Verify admin credentials using hash (prod) or plain password (dev/test)."""
    if settings.auth_admin_password_hash:
        return verify_password(password, settings.auth_admin_password_hash)
    if settings.auth_admin_password and not settings.is_production:
        return password == settings.auth_admin_password
    return False


@router.post(
    "/token",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtain access token",
    description="Exchange credentials for a JWT access token.",
)
async def login_for_access_token(
    request: TokenRequest,
    settings: Annotated[Settings, Depends(get_settings_dependency)],
) -> TokenResponse:
    """Issue a JWT access token for valid credentials."""
    if request.username != settings.auth_default_username:
        raise AuthenticationError("Invalid username or password")

    if not _verify_admin_credentials(request.password, settings):
        raise AuthenticationError("Invalid username or password")

    token = create_access_token(subject=request.username, settings=settings)
    return TokenResponse(
        access_token=token,
        expires_in_minutes=settings.access_token_expire_minutes,
    )
