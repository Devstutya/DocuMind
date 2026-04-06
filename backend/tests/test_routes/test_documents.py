# backend/tests/test_routes/test_documents.py
"""
Integration tests for /api/documents endpoints.

Covers:
- POST /api/documents/upload  — happy path, non-PDF rejection, missing auth,
                                 oversized file
- GET  /api/documents/         — lists only the caller's documents
- DELETE /api/documents/{id}   — happy path, not found, wrong owner
"""

import io

import fitz  # PyMuPDF — used to create minimal in-memory PDFs for testing
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

UPLOAD_URL = "/api/documents/upload"
LIST_URL = "/api/documents/"
REGISTER_URL = "/api/auth/register"

_USER_A = {"email": "alice@example.com", "username": "alice", "password": "secret123"}
_USER_B = {"email": "bob@example.com", "username": "bob", "password": "secret456"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _register_and_login(client: AsyncClient, payload: dict) -> str:
    """Register a user and return the JWT access token."""
    resp = await client.post(REGISTER_URL, json=payload)
    assert resp.status_code == 201, resp.text
    return resp.json()["access_token"]


def _make_pdf(text: str = "Hello DocuMind test page.") -> bytes:
    """Create a minimal single-page PDF in memory using PyMuPDF.

    This avoids any dependency on fixture files on disk.
    """
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), text)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


def _pdf_upload_file(filename: str = "test.pdf", text: str = "Hello DocuMind test page."):
    """Return the (files, ...) tuple suitable for httpx multipart upload."""
    return ("file", (filename, io.BytesIO(_make_pdf(text)), "application/pdf"))


def _auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# Upload tests
# ---------------------------------------------------------------------------


async def test_upload_pdf_success(client: AsyncClient):
    """Happy path: authenticated user uploads a valid PDF and receives metadata."""
    token = await _register_and_login(client, _USER_A)

    resp = await client.post(
        UPLOAD_URL,
        files=[_pdf_upload_file()],
        headers=_auth_headers(token),
    )

    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["filename"] == "test.pdf"
    assert body["status"] == "processed"
    assert body["page_count"] >= 1
    assert body["chunk_count"] >= 1
    assert "document_id" in body
    assert body["message"]


async def test_upload_non_pdf_returns_400(client: AsyncClient):
    """Uploading a plain-text file must be rejected with 400."""
    token = await _register_and_login(client, _USER_A)

    resp = await client.post(
        UPLOAD_URL,
        files=[("file", ("notes.txt", io.BytesIO(b"just text"), "text/plain"))],
        headers=_auth_headers(token),
    )

    assert resp.status_code == 400
    assert "pdf" in resp.json()["detail"].lower()


async def test_upload_without_auth_returns_401_or_403(client: AsyncClient):
    """Request without a Bearer token must be rejected."""
    resp = await client.post(
        UPLOAD_URL,
        files=[_pdf_upload_file()],
    )

    assert resp.status_code in (401, 403)


async def test_upload_with_invalid_token_returns_401(client: AsyncClient):
    """A garbage token must be rejected."""
    resp = await client.post(
        UPLOAD_URL,
        files=[_pdf_upload_file()],
        headers={"Authorization": "Bearer thisisnotalidtoken"},
    )

    assert resp.status_code == 401


async def test_upload_oversized_file_returns_400(client: AsyncClient, monkeypatch):
    """A file that exceeds MAX_FILE_SIZE_MB must be rejected with 400."""
    from app.config import settings

    token = await _register_and_login(client, _USER_A)

    # Temporarily lower the limit to 0 MB so any file triggers the check.
    monkeypatch.setattr(settings, "MAX_FILE_SIZE_MB", 0)

    resp = await client.post(
        UPLOAD_URL,
        files=[_pdf_upload_file()],
        headers=_auth_headers(token),
    )

    assert resp.status_code == 400
    assert "size" in resp.json()["detail"].lower() or "mb" in resp.json()["detail"].lower()


# ---------------------------------------------------------------------------
# List tests
# ---------------------------------------------------------------------------


async def test_list_returns_empty_for_new_user(client: AsyncClient):
    """A newly registered user has no documents."""
    token = await _register_and_login(client, _USER_A)

    resp = await client.get(LIST_URL, headers=_auth_headers(token))

    assert resp.status_code == 200
    body = resp.json()
    assert body["documents"] == []
    assert body["total"] == 0


async def test_list_returns_owned_documents_only(client: AsyncClient):
    """Each user sees only their own documents — not those of other users."""
    token_a = await _register_and_login(client, _USER_A)
    token_b = await _register_and_login(client, _USER_B)

    # Alice uploads two documents.
    for name in ("a1.pdf", "a2.pdf"):
        resp = await client.post(
            UPLOAD_URL,
            files=[_pdf_upload_file(filename=name)],
            headers=_auth_headers(token_a),
        )
        assert resp.status_code == 201, resp.text

    # Bob uploads one document.
    resp = await client.post(
        UPLOAD_URL,
        files=[_pdf_upload_file(filename="b1.pdf")],
        headers=_auth_headers(token_b),
    )
    assert resp.status_code == 201, resp.text

    # Alice should see exactly her 2 documents.
    resp_a = await client.get(LIST_URL, headers=_auth_headers(token_a))
    assert resp_a.status_code == 200
    body_a = resp_a.json()
    assert body_a["total"] == 2
    filenames_a = {d["filename"] for d in body_a["documents"]}
    assert filenames_a == {"a1.pdf", "a2.pdf"}

    # Bob should see exactly his 1 document.
    resp_b = await client.get(LIST_URL, headers=_auth_headers(token_b))
    assert resp_b.status_code == 200
    body_b = resp_b.json()
    assert body_b["total"] == 1
    assert body_b["documents"][0]["filename"] == "b1.pdf"


async def test_list_without_auth_returns_401_or_403(client: AsyncClient):
    """Unauthenticated list request must be rejected."""
    resp = await client.get(LIST_URL)

    assert resp.status_code in (401, 403)


# ---------------------------------------------------------------------------
# Delete tests
# ---------------------------------------------------------------------------


async def _upload_doc(client: AsyncClient, token: str, filename: str = "doc.pdf") -> str:
    """Upload a PDF and return the document_id."""
    resp = await client.post(
        UPLOAD_URL,
        files=[_pdf_upload_file(filename=filename)],
        headers=_auth_headers(token),
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["document_id"]


async def test_delete_document_happy_path(client: AsyncClient):
    """Owner can delete their document; subsequent list shows it gone."""
    token = await _register_and_login(client, _USER_A)
    doc_id = await _upload_doc(client, token)

    resp = await client.delete(f"/api/documents/{doc_id}", headers=_auth_headers(token))
    assert resp.status_code == 204

    # Confirm it is no longer listed.
    list_resp = await client.get(LIST_URL, headers=_auth_headers(token))
    assert list_resp.json()["total"] == 0


async def test_delete_nonexistent_document_returns_404(client: AsyncClient):
    """Deleting an unknown document_id must return 404."""
    token = await _register_and_login(client, _USER_A)

    resp = await client.delete(
        "/api/documents/00000000-0000-0000-0000-000000000000",
        headers=_auth_headers(token),
    )

    assert resp.status_code == 404


async def test_delete_other_users_document_returns_403(client: AsyncClient):
    """Attempting to delete another user's document must return 403, not 404."""
    token_a = await _register_and_login(client, _USER_A)
    token_b = await _register_and_login(client, _USER_B)

    # Alice uploads a document.
    doc_id = await _upload_doc(client, token_a, filename="alice_doc.pdf")

    # Bob tries to delete Alice's document.
    resp = await client.delete(
        f"/api/documents/{doc_id}",
        headers=_auth_headers(token_b),
    )

    assert resp.status_code == 403

    # Alice's document must still be present.
    list_resp = await client.get(LIST_URL, headers=_auth_headers(token_a))
    assert list_resp.json()["total"] == 1


async def test_delete_without_auth_returns_401_or_403(client: AsyncClient):
    """Unauthenticated delete must be rejected."""
    resp = await client.delete("/api/documents/some-id")

    assert resp.status_code in (401, 403)
