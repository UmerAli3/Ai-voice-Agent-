"""SQLAlchemy Async Database connection setup & engine management."""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from src.app.core.config import settings
from src.app.core.logging import logger

# Async SQLAlchemy Engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# Async Session Factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """Base ORM model class."""
    pass


async def init_db() -> None:
    """Startup initialization check for database connection pool."""
    logger.info("Initializing async database connection pool...", url=settings.POSTGRES_SERVER)


async def close_db() -> None:
    """Gracefully dispose database connection engine pool on shutdown."""
    logger.info("Closing async database connection pool...")
    await engine.dispose()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for providing async database session to route handlers."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
