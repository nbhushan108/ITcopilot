"""Async database session management."""

from collections.abc import AsyncGenerator

from loguru import logger
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.exceptions import DatabaseError
from app.core.settings import Settings, get_settings
from app.db.base import Base

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None
_engine_url: str | None = None


def create_engine(settings: Settings | None = None) -> AsyncEngine:
    """Create and configure the async SQLAlchemy engine.

    Args:
        settings: Optional settings override.

    Returns:
        Configured AsyncEngine instance.

    Raises:
        DatabaseError: If engine creation fails.
    """
    app_settings = settings or get_settings()
    try:
        engine_kwargs: dict[str, object] = {
            "echo": app_settings.database_echo,
            "pool_pre_ping": True,
        }

        if "sqlite" not in app_settings.database_url:
            engine_kwargs["pool_size"] = app_settings.database_pool_size
            engine_kwargs["max_overflow"] = app_settings.database_max_overflow

        return create_async_engine(app_settings.database_url, **engine_kwargs)
    except Exception as exc:
        logger.error("Failed to create database engine: {}", exc)
        raise DatabaseError("Database engine initialization failed") from exc


def get_engine(settings: Settings | None = None) -> AsyncEngine:
    """Return the application database engine singleton.

    Args:
        settings: Optional settings override for engine URL.

    Returns:
        AsyncEngine bound to configured database URL.
    """
    global _engine, _engine_url
    app_settings = settings or get_settings()
    if _engine is None or _engine_url != app_settings.database_url:
        _engine = create_engine(app_settings)
        _engine_url = app_settings.database_url
    return _engine


def get_session_factory(settings: Settings | None = None) -> async_sessionmaker[AsyncSession]:
    """Return the async session factory singleton.

    Args:
        settings: Optional settings override.

    Returns:
        Configured async session factory.
    """
    global _session_factory, _engine_url
    app_settings = settings or get_settings()
    if _session_factory is None or _engine_url != app_settings.database_url:
        _session_factory = async_sessionmaker(
            bind=get_engine(app_settings),
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
        )
    return _session_factory


def reset_engine_cache() -> None:
    """Reset engine and session factory singletons (for testing)."""
    global _engine, _session_factory, _engine_url
    _engine = None
    _session_factory = None
    _engine_url = None


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async database session with automatic cleanup.

    Yields:
        Active AsyncSession instance.

    Raises:
        DatabaseError: If session operations fail unexpectedly.
    """
    session_factory = get_session_factory()
    session = session_factory()
    try:
        yield session
        await session.commit()
    except Exception as exc:
        await session.rollback()
        logger.error("Database session error: {}", exc)
        raise DatabaseError("Database operation failed") from exc
    finally:
        await session.close()


async def check_database_connectivity() -> bool:
    """Verify database connectivity with a simple query.

    Returns:
        True if database is reachable.
    """
    try:
        engine = get_engine()
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception as exc:
        logger.error("Database connectivity check failed: {}", exc)
        return False


async def init_db(settings: Settings | None = None) -> None:
    """Initialize database schema when auto-create is enabled.

    In production, schema changes must be applied via Alembic migrations.

    Args:
        settings: Optional settings override.

    Raises:
        DatabaseError: If schema initialization fails.
    """
    app_settings = settings or get_settings()
    if not app_settings.auto_create_schema:
        logger.info("Skipping auto schema creation; use Alembic migrations")
        return

    try:
        engine = get_engine(app_settings)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database schema initialized successfully (auto-create)")
    except Exception as exc:
        logger.error("Database initialization failed: {}", exc)
        raise DatabaseError("Database schema initialization failed") from exc
