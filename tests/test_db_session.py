"""Database session management unit tests."""

from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DatabaseError
from app.core.settings import Environment, Settings
from app.db.session import (
    check_database_connectivity,
    create_engine,
    get_engine,
    get_session_factory,
    init_db,
    reset_engine_cache,
)


@pytest.fixture(autouse=True)
def _reset_cache() -> None:
    """Reset engine singleton between tests."""
    reset_engine_cache()


@pytest.mark.unit
class TestDatabaseSession:
    """Tests for async database session helpers."""

    def test_create_engine_sqlite(self) -> None:
        """SQLite engine should be created without pool settings."""
        settings = Settings(
            environment=Environment.TESTING,
            database_url="sqlite+aiosqlite:///:memory:",
            secret_key="test-secret-key-not-for-production-use-only-32chars",
        )
        engine = create_engine(settings)
        assert engine is not None

    def test_create_engine_postgresql_uses_pool(self) -> None:
        """PostgreSQL engine should include pool configuration."""
        settings = Settings(
            environment=Environment.TESTING,
            database_url="postgresql+asyncpg://user:pass@localhost/db",
            secret_key="test-secret-key-not-for-production-use-only-32chars",
        )
        engine = create_engine(settings)
        assert engine is not None

    def test_create_engine_failure_raises_database_error(self) -> None:
        """Engine creation failures should raise DatabaseError."""
        settings = Settings(
            environment=Environment.TESTING,
            database_url="invalid://not-a-real-driver",
            secret_key="test-secret-key-not-for-production-use-only-32chars",
        )
        with pytest.raises(DatabaseError, match="Database engine initialization failed"):
            create_engine(settings)

    def test_get_engine_singleton_and_reset(self) -> None:
        """get_engine should cache and reset_engine_cache should clear."""
        settings = Settings(
            environment=Environment.TESTING,
            database_url="sqlite+aiosqlite:///:memory:",
            secret_key="test-secret-key-not-for-production-use-only-32chars",
        )
        first = get_engine(settings)
        second = get_engine(settings)
        assert first is second
        reset_engine_cache()
        third = get_engine(settings)
        assert third is not first

    def test_get_session_factory(self) -> None:
        """Session factory should be created for valid engine."""
        settings = Settings(
            environment=Environment.TESTING,
            database_url="sqlite+aiosqlite:///:memory:",
            secret_key="test-secret-key-not-for-production-use-only-32chars",
        )
        factory = get_session_factory(settings)
        assert factory is not None

    @pytest.mark.asyncio
    async def test_check_database_connectivity_success(self) -> None:
        """Connectivity check should pass for in-memory sqlite."""
        settings = Settings(
            environment=Environment.TESTING,
            database_url="sqlite+aiosqlite:///:memory:",
            secret_key="test-secret-key-not-for-production-use-only-32chars",
        )
        get_engine(settings)
        assert await check_database_connectivity() is True

    @pytest.mark.asyncio
    async def test_check_database_connectivity_failure(self) -> None:
        """Connectivity check should return False on connection errors."""
        reset_engine_cache()
        with patch("app.db.session.get_engine", side_effect=RuntimeError("db down")):
            assert await check_database_connectivity() is False

    @pytest.mark.asyncio
    async def test_init_db_skips_when_auto_create_disabled(self) -> None:
        """init_db should skip schema creation when auto_create_schema is false."""
        settings = Settings(
            environment=Environment.PRODUCTION,
            database_url="sqlite+aiosqlite:///:memory:",
            secret_key="a" * 32,
            debug=False,
            auto_create_schema=False,
            auth_admin_password_hash="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        )
        await init_db(settings)

    @pytest.mark.asyncio
    async def test_init_db_creates_schema(self) -> None:
        """init_db should create tables when auto_create_schema is enabled."""
        settings = Settings(
            environment=Environment.TESTING,
            database_url="sqlite+aiosqlite:///:memory:",
            secret_key="test-secret-key-not-for-production-use-only-32chars",
            auto_create_schema=True,
        )
        await init_db(settings)

    @pytest.mark.asyncio
    async def test_get_db_session_rollback_on_error(self) -> None:
        """get_db_session should rollback and raise DatabaseError on commit failure."""
        from unittest.mock import AsyncMock

        mock_session = AsyncMock(spec=AsyncSession)
        mock_session.commit.side_effect = RuntimeError("commit failed")
        mock_factory = MagicMock(return_value=mock_session)

        with patch("app.db.session.get_session_factory", return_value=mock_factory):
            from app.db.session import get_db_session

            with pytest.raises(DatabaseError, match="Database operation failed"):
                async for _ in get_db_session():
                    pass
