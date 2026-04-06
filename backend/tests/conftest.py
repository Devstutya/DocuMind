# backend/tests/conftest.py
import os

# Set required environment variables BEFORE importing the app so that
# pydantic-settings can construct the Settings object without a real .env file.
# These values are only used for testing — they are not real credentials.
os.environ.setdefault("OPENAI_API_KEY", "sk-test-openai-key")
os.environ.setdefault("PINECONE_API_KEY", "test-pinecone-key")
os.environ.setdefault("JWT_SECRET_KEY", "test-jwt-secret-key-for-unit-tests-only")
# Use an in-memory SQLite database so tests are fully isolated and leave no
# files on disk.
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.database import Base, get_db
from app.main import app as fastapi_app

# ---------------------------------------------------------------------------
# Per-test in-memory database engine and session override
# ---------------------------------------------------------------------------

_TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def client(tmp_path) -> AsyncClient:
    """Async HTTP client wired directly to the FastAPI app.

    Each test gets its own in-memory SQLite database so there is zero state
    leakage between tests.  The ``get_db`` dependency is overridden to use a
    session backed by a fresh engine for the duration of the test.
    """
    # Import ORM models so they register themselves with Base.
    import app.db_models  # noqa: F401

    test_engine = create_async_engine(_TEST_DATABASE_URL, echo=False)

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    TestSessionLocal = async_sessionmaker(test_engine, expire_on_commit=False)

    async def override_get_db():
        async with TestSessionLocal() as session:
            yield session

    fastapi_app.dependency_overrides[get_db] = override_get_db

    # Redirect uploads to a fresh temp directory for each test.
    original_upload_dir = settings.UPLOAD_DIR
    settings.UPLOAD_DIR = str(tmp_path)

    async with AsyncClient(
        transport=ASGITransport(app=fastapi_app), base_url="http://test"
    ) as ac:
        yield ac

    # Teardown: restore state, drop tables, dispose engine.
    settings.UPLOAD_DIR = original_upload_dir
    fastapi_app.dependency_overrides.pop(get_db, None)

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await test_engine.dispose()
