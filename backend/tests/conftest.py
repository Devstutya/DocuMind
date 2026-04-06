# backend/tests/conftest.py
import os
import shutil
import tempfile

# Set required environment variables BEFORE importing the app so that
# pydantic-settings can construct the Settings object without a real .env file.
# These values are only used for testing — they are not real credentials.
os.environ.setdefault("OPENAI_API_KEY", "sk-test-openai-key")
os.environ.setdefault("PINECONE_API_KEY", "test-pinecone-key")
os.environ.setdefault("JWT_SECRET_KEY", "test-jwt-secret-key-for-unit-tests-only")

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.auth import routes as auth_routes_module
from app.documents import routes as documents_routes_module
from app.config import settings


@pytest_asyncio.fixture
async def client() -> AsyncClient:
    """Async HTTP client wired directly to the FastAPI app (no network calls)."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture(autouse=True)
def reset_stores(tmp_path):
    """Clear all in-memory stores and point UPLOAD_DIR at a temp directory.

    Using a per-test temp directory keeps uploaded files isolated and avoids
    leftover files on disk between test runs.
    """
    auth_routes_module._users.clear()
    documents_routes_module._documents.clear()

    # Redirect uploads to a fresh temp directory for each test.
    original_upload_dir = settings.UPLOAD_DIR
    settings.UPLOAD_DIR = str(tmp_path)

    yield

    # Restore original value and clear stores again for safety.
    settings.UPLOAD_DIR = original_upload_dir
    auth_routes_module._users.clear()
    documents_routes_module._documents.clear()
