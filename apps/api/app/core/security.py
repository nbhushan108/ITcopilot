"""JWT authentication and password utilities."""

from datetime import UTC, datetime, timedelta
from typing import Any

import bcrypt
from jose import JWTError, jwt
from loguru import logger

from app.core.exceptions import AuthenticationError
from app.core.settings import Settings


ALGORITHM = "HS256"


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
    return str(jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM))


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
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        subject = payload.get("sub")
        if not isinstance(subject, str) or not subject:
            raise AuthenticationError("Invalid token payload")
        return subject
    except JWTError as exc:
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
