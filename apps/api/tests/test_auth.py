"""Authentication API integration tests."""

import pytest
from httpx import AsyncClient

from app.core.security import hash_password
from app.core.settings import Environment, Settings
from app.routers.auth import _verify_admin_credentials


@pytest.mark.integration
class TestAuthEndpoints:
    """Tests for /api/v1/auth endpoints."""

    async def test_token_invalid_credentials(self, client: AsyncClient) -> None:
        """Invalid credentials should return 401."""
        response = await client.post(
            "/api/v1/auth/token",
            json={"username": "admin", "password": "wrong-password"},
        )
        assert response.status_code == 401

    async def test_token_valid_credentials(self, client: AsyncClient) -> None:
        """Valid dev credentials should return access token."""
        response = await client.post(
            "/api/v1/auth/token",
            json={"username": "admin", "password": "secret"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    async def test_token_invalid_username(self, client: AsyncClient) -> None:
        """Invalid username should return 401."""
        response = await client.post(
            "/api/v1/auth/token",
            json={"username": "wrong-user", "password": "secret"},
        )
        assert response.status_code == 401

    def test_verify_admin_credentials_with_hash(self) -> None:
        """Production-style bcrypt hash authentication should work."""
        password_hash = hash_password("hash-only-password")
        settings = Settings(
            environment=Environment.TESTING,
            secret_key="test-secret-key-not-for-production-use-only-32chars",
            auth_admin_password_hash=password_hash,
        )
        assert _verify_admin_credentials("hash-only-password", settings)
        assert not _verify_admin_credentials("wrong", settings)
