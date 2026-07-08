#!/usr/bin/env python3
"""Database initialization script."""

import asyncio
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "apps" / "api"))

from loguru import logger

from app.core.logging import configure_logging
from app.core.settings import get_settings
from app.db.session import init_db


async def main() -> None:
    """Initialize the database schema."""
    settings = get_settings()
    configure_logging(settings)

    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)

    logger.info("Initializing database at {}", settings.database_url)
    await init_db()
    logger.info("Database initialization complete")


if __name__ == "__main__":
    asyncio.run(main())
