"""Authentication request and response schemas."""

from pydantic import BaseModel, Field


class TokenRequest(BaseModel):
    """Request schema for obtaining an access token."""

    username: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=1, max_length=128)


class TokenResponse(BaseModel):
    """Response schema containing a JWT access token."""

    access_token: str
    token_type: str = "bearer"
    expires_in_minutes: int


class CurrentUser(BaseModel):
    """Authenticated user context."""

    username: str
