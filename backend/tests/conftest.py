# backend/tests/conftest.py
import os

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


@pytest_asyncio.fixture
async def client() -> AsyncClient:
    """Async HTTP client wired directly to the FastAPI app (no network calls)."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture(autouse=True)
def reset_user_store():
    """Clear the in-memory user store before every test to ensure isolation."""
    auth_routes_module._users.clear()
    yield
    auth_routes_module._users.clear()
