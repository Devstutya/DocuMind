# backend/app/database.py
"""Async SQLAlchemy engine, session factory, and base declarative class.

In development the app creates tables via ``Base.metadata.create_all`` in the
lifespan hook (see main.py).  In production, use Alembic migrations instead.
"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=False)

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    """Shared declarative base for all ORM models."""
    pass


async def get_db():
    """FastAPI dependency that yields an ``AsyncSession`` per request."""
    async with AsyncSessionLocal() as session:
        yield session
