"""Security module unit tests."""

from datetime import timedelta

import jwt
import pytest

from app.core.exceptions import AuthenticationError
from app.core.security import (
    ALGORITHM,
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from app.core.settings import Environment, Settings


@pytest.mark.unit
class TestSecurity:
    """Tests for JWT and password utilities."""

    @pytest.fixture
    def settings(self) -> Settings:
        """Provide test settings with secret key."""
        return Settings(
            environment=Environment.TESTING,
            secret_key="test-secret-key-not-for-production-use-only-32chars",
            access_token_expire_minutes=30,
        )

    def test_hash_and_verify_password(self) -> None:
        """hash_password and verify_password should round-trip."""
        hashed = hash_password("my-secure-password")
        assert verify_password("my-secure-password", hashed)
        assert not verify_password("wrong-password", hashed)

    def test_create_and_decode_access_token(self, settings: Settings) -> None:
        """JWT tokens should encode and decode the subject."""
        token = create_access_token("admin", settings)
        assert decode_access_token(token, settings) == "admin"

    def test_decode_invalid_token(self, settings: Settings) -> None:
        """Invalid tokens should raise AuthenticationError."""
        with pytest.raises(AuthenticationError, match="Invalid or expired token"):
            decode_access_token("not-a-valid-jwt", settings)

    def test_decode_token_with_custom_expiry(self, settings: Settings) -> None:
        """Custom expiry delta should be accepted."""
        token = create_access_token(
            "admin",
            settings,
            expires_delta=timedelta(minutes=5),
        )
        assert decode_access_token(token, settings) == "admin"

    def test_decode_token_missing_subject(self, settings: Settings) -> None:
        """Tokens without a subject should be rejected."""
        token = jwt.encode({"exp": 9999999999}, settings.secret_key, algorithm=ALGORITHM)
        with pytest.raises(AuthenticationError, match="Invalid token payload"):
            decode_access_token(token, settings)
