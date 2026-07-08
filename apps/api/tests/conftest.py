"""Pytest configuration and shared fixtures."""

import os
from collections.abc import AsyncGenerator, Generator
from typing import Any

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.settings import Environment, Settings, get_settings
from app.db.base import Base
from app.db.session import reset_engine_cache
from app.main import create_app


@pytest.fixture(scope="session")
def test_settings() -> Settings:
    """Provide test-specific application settings."""
    os.environ["ENVIRONMENT"] = "testing"
    os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
    os.environ["SECRET_KEY"] = "test-secret-key-not-for-production-use-only-32chars"
    os.environ["AUTH_ENABLED"] = "false"
    os.environ["AUTO_CREATE_SCHEMA"] = "true"
    get_settings.cache_clear()
    reset_engine_cache()
    return Settings(
        environment=Environment.TESTING,
        database_url="sqlite+aiosqlite:///:memory:",
        secret_key="test-secret-key-not-for-production-use-only-32chars",
        auth_enabled=False,
        auth_admin_password="secret",
        auto_create_schema=True,
        debug=True,
    )


@pytest.fixture
async def test_engine(test_settings: Settings) -> AsyncGenerator[AsyncEngine, None]:
    """Provide an isolated in-memory database engine for each test."""
    engine = create_async_engine(test_settings.database_url, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine
    await engine.dispose()


@pytest.fixture
async def db_session(test_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """Provide an isolated in-memory database session for each test."""
    session_factory = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with session_factory() as session:
        yield session


@pytest.fixture
def app(test_settings: Settings, test_engine: AsyncEngine) -> Generator[Any, None, None]:
    """Provide configured FastAPI application with test database override."""
    session_factory = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        session = session_factory()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    from app.core.dependencies import get_db, get_settings_dependency

    application = create_app(settings=test_settings)
    application.dependency_overrides[get_db] = override_get_db
    application.dependency_overrides[get_settings_dependency] = lambda: test_settings
    yield application
    application.dependency_overrides.clear()


@pytest.fixture
async def client(app: Any) -> AsyncGenerator[AsyncClient, None]:
    """Provide async HTTP test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
