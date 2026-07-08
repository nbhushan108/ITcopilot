"""JWT authentication and password utilities."""

from datetime import UTC, datetime, timedelta
from typing import Any

import bcrypt
import jwt
from jwt.exceptions import PyJWTError
from loguru import logger

from app.core.exceptions import AuthenticationError
from app.core.settings import Settings
from common.config.constants import DEFAULT_JWT_ALGORITHM

ALGORITHM = DEFAULT_JWT_ALGORITHM


def create_access_token(
    subject: str,
    settings: Settings,
    expires_delta: timedelta | None = None,
) -> str:
    """Create a signed JWT access token.

    Args:
        subject: Token subject (typically username or user ID).
        settings: Application settings with secret key.
        expires_delta: Optional custom expiration duration.

    Returns:
        Encoded JWT string.
    """
    expire = datetime.now(tz=UTC) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    payload: dict[str, Any] = {
        "sub": subject,
        "exp": expire,
        "iat": datetime.now(tz=UTC),
    }
    secret = settings.jwt_secret or settings.secret_key
    return str(jwt.encode(payload, secret, algorithm=settings.jwt_algorithm))


def decode_access_token(token: str, settings: Settings) -> str:
    """Decode and validate a JWT access token.

    Args:
        token: Encoded JWT string.
        settings: Application settings with secret key.

    Returns:
        Token subject (username).

    Raises:
        AuthenticationError: If token is invalid or expired.
    """
    try:
        secret = settings.jwt_secret or settings.secret_key
        payload = jwt.decode(token, secret, algorithms=[settings.jwt_algorithm])
        subject = payload.get("sub")
        if not isinstance(subject, str) or not subject:
            raise AuthenticationError("Invalid token payload")
        return subject
    except PyJWTError as exc:
        logger.warning("JWT validation failed: {}", exc)
        raise AuthenticationError("Invalid or expired token") from exc


def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt.

    Args:
        password: Plaintext password.

    Returns:
        Bcrypt hash string.
    """
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a hash.

    Args:
        plain_password: Plaintext password.
        hashed_password: Stored bcrypt hash.

    Returns:
        True if password matches.
    """
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )
