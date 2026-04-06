# backend/tests/test_routes/test_auth.py
"""
Integration tests for /api/auth endpoints.

Covers:
- POST /api/auth/register  — happy path, duplicate username, duplicate email
- POST /api/auth/login     — happy path, wrong password, unknown user
- GET  /api/auth/me        — valid token, missing token, malformed token
"""

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

REGISTER_URL = "/api/auth/register"
LOGIN_URL = "/api/auth/login"
ME_URL = "/api/auth/me"

VALID_USER = {
    "email": "alice@example.com",
    "username": "alice",
    "password": "supersecret",
}


async def _register_and_get_token(client: AsyncClient, payload: dict = None) -> str:
    """Register a user and return the access token."""
    payload = payload or VALID_USER
    resp = await client.post(REGISTER_URL, json=payload)
    assert resp.status_code == 201, resp.text
    return resp.json()["access_token"]


# ---------------------------------------------------------------------------
# Registration tests
# ---------------------------------------------------------------------------


async def test_register_success_returns_token(client: AsyncClient):
    """Happy path: new user receives a JWT access token."""
    resp = await client.post(REGISTER_URL, json=VALID_USER)

    assert resp.status_code == 201
    body = resp.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"
    assert len(body["access_token"]) > 0


async def test_register_duplicate_username_returns_409(client: AsyncClient):
    """Second registration with the same username must be rejected."""
    await client.post(REGISTER_URL, json=VALID_USER)

    duplicate = {**VALID_USER, "email": "other@example.com"}
    resp = await client.post(REGISTER_URL, json=duplicate)

    assert resp.status_code == 409
    assert "username" in resp.json()["detail"].lower()


async def test_register_duplicate_email_returns_409(client: AsyncClient):
    """Second registration with the same email address must be rejected."""
    await client.post(REGISTER_URL, json=VALID_USER)

    duplicate = {**VALID_USER, "username": "alice2"}
    resp = await client.post(REGISTER_URL, json=duplicate)

    assert resp.status_code == 409
    assert "email" in resp.json()["detail"].lower()


async def test_register_invalid_email_returns_422(client: AsyncClient):
    """Pydantic must reject a malformed email address before it hits the handler."""
    resp = await client.post(
        REGISTER_URL,
        json={"email": "not-an-email", "username": "alice", "password": "secret"},
    )

    assert resp.status_code == 422


async def test_register_missing_fields_returns_422(client: AsyncClient):
    """Request body missing required fields must return 422."""
    resp = await client.post(REGISTER_URL, json={"username": "alice"})

    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Login tests
# ---------------------------------------------------------------------------


async def test_login_success_returns_token(client: AsyncClient):
    """Registered user can log in and receive a valid token."""
    await _register_and_get_token(client)

    resp = await client.post(
        LOGIN_URL,
        json={"username": VALID_USER["username"], "password": VALID_USER["password"]},
    )

    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


async def test_login_wrong_password_returns_401(client: AsyncClient):
    """Wrong password must return 401, not 403 or 404."""
    await _register_and_get_token(client)

    resp = await client.post(
        LOGIN_URL,
        json={"username": VALID_USER["username"], "password": "wrongpassword"},
    )

    assert resp.status_code == 401


async def test_login_unknown_username_returns_401(client: AsyncClient):
    """Unknown username must return 401 (not 404, to avoid account enumeration)."""
    resp = await client.post(
        LOGIN_URL,
        json={"username": "nobody", "password": "anypassword"},
    )

    assert resp.status_code == 401


async def test_login_missing_fields_returns_422(client: AsyncClient):
    """Login request missing password must return 422."""
    resp = await client.post(LOGIN_URL, json={"username": "alice"})

    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Protected route tests (GET /me)
# ---------------------------------------------------------------------------


async def test_me_valid_token_returns_user(client: AsyncClient):
    """Valid Bearer token returns the authenticated user's profile."""
    token = await _register_and_get_token(client)

    resp = await client.get(ME_URL, headers={"Authorization": f"Bearer {token}"})

    assert resp.status_code == 200
    body = resp.json()
    assert body["username"] == VALID_USER["username"]
    assert body["email"] == VALID_USER["email"]
    assert "id" in body
    assert "created_at" in body
    # Password must never appear in the response
    assert "password" not in body
    assert "hashed_password" not in body


async def test_me_missing_token_returns_401(client: AsyncClient):
    """Request without Authorization header must be rejected (401 or 403)."""
    resp = await client.get(ME_URL)

    assert resp.status_code in (401, 403)


async def test_me_malformed_token_returns_401(client: AsyncClient):
    """Garbage token value must be rejected with 401."""
    resp = await client.get(ME_URL, headers={"Authorization": "Bearer notavalidtoken"})

    assert resp.status_code == 401


async def test_me_tampered_token_returns_401(client: AsyncClient):
    """Token with invalid signature must be rejected."""
    token = await _register_and_get_token(client)
    # Flip the last character to corrupt the signature
    tampered = token[:-1] + ("A" if token[-1] != "A" else "B")

    resp = await client.get(ME_URL, headers={"Authorization": f"Bearer {tampered}"})

    assert resp.status_code == 401
