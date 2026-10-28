"""database.py — Finance service async database engine and session factory."""
import os
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_SQLITE_URL = f"sqlite+aiosqlite:///{REPO_ROOT / 'zenkai.db'}"

DATABASE_URL = os.environ.get("DATABASE_URL", DEFAULT_SQLITE_URL)

if DATABASE_URL.startswith("sqlite"):
    engine = create_async_engine(DATABASE_URL, echo=False)
else:
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
        pool_size=2,
        max_overflow=3,
    )

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    """FastAPI dependency — yields an async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
