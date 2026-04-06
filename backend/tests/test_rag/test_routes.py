# backend/tests/test_rag/test_routes.py
"""
Integration tests for /api/rag endpoints.

All LLM and Pinecone calls are mocked so tests run without real credentials
and without hitting external services.

Covers:
- POST /api/rag/query  — happy path, missing auth, document_ids filter,
                          follow-up with conversation history, empty chunks
- GET  /api/rag/conversations/{id} — returns history, 404 for unknown id
"""

import io
from unittest.mock import AsyncMock, patch

import fitz
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

QUERY_URL = "/api/rag/query"
REGISTER_URL = "/api/auth/register"

_FAKE_EMBEDDING: list[float] = [0.1] * 1536

_FAKE_CHUNKS = [
    {
        "id": "doc_abc_0",
        "score": 0.92,
        "text": "Relevant chunk text from the document.",
        "page": 3,
        "doc_id": "doc_abc",
    },
    {
        "id": "doc_abc_1",
        "score": 0.85,
        "text": "Another relevant chunk.",
        "page": 5,
        "doc_id": "doc_abc",
    },
]

_USER = {"email": "rag@example.com", "username": "raguser", "password": "ragpassword1"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _register_and_get_token(client: AsyncClient, payload: dict = None) -> str:
    """Register a user and return the JWT access token."""
    payload = payload or _USER
    resp = await client.post(REGISTER_URL, json=payload)
    assert resp.status_code == 201, resp.text
    return resp.json()["access_token"]


def _auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _make_pdf_bytes(text: str = "Hello DocuMind test.") -> bytes:
    """Create a minimal in-memory PDF using PyMuPDF."""
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), text)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


async def _upload_document(client: AsyncClient, token: str, doc_id_override: str = "doc_abc") -> str:
    """Upload a PDF and return the document_id, mocking external calls."""
    with (
        patch("app.documents.routes.get_embeddings", return_value=[_FAKE_EMBEDDING]),
        patch("app.documents.routes.upsert_chunks", return_value=None),
    ):
        resp = await client.post(
            "/api/documents/upload",
            files=[("file", ("test.pdf", io.BytesIO(_make_pdf_bytes()), "application/pdf"))],
            headers=_auth_headers(token),
        )
    assert resp.status_code == 201, resp.text
    return resp.json()["document_id"]


def _mock_rag_externals(
    chunks: list[dict] | None = None,
    answer: str = "Mocked answer",
):
    """Return patch context managers for embeddings, query_similar, and generate_answer."""
    if chunks is None:
        chunks = _FAKE_CHUNKS

    patch_embeddings = patch(
        "app.rag.routes.get_embeddings",
        return_value=[_FAKE_EMBEDDING],
    )
    patch_query = patch(
        "app.rag.routes.query_similar",
        return_value=chunks,
    )
    patch_answer = patch(
        "app.rag.routes.generate_answer",
        new=AsyncMock(return_value=answer),
    )
    return patch_embeddings, patch_query, patch_answer


# ---------------------------------------------------------------------------
# POST /api/rag/query — happy path
# ---------------------------------------------------------------------------


async def test_query_happy_path_returns_answer_and_sources(client: AsyncClient):
    """Authenticated query returns an answer with source citations."""
    token = await _register_and_get_token(client)
    real_doc_id = await _upload_document(client, token)

    # Patch chunks so their doc_id matches the real uploaded document.
    chunks_with_real_id = [
        {**_FAKE_CHUNKS[0], "doc_id": real_doc_id},
        {**_FAKE_CHUNKS[1], "doc_id": real_doc_id},
    ]

    pe, pq, pa = _mock_rag_externals(chunks=chunks_with_real_id, answer="Mocked answer")
    with pe, pq, pa:
        resp = await client.post(
            QUERY_URL,
            json={"question": "What is the refund policy?"},
            headers=_auth_headers(token),
        )

    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["answer"] == "Mocked answer"
    assert "conversation_id" in body
    assert body["query_time_ms"] >= 0

    # Sources must contain our mocked chunks.
    assert len(body["sources"]) == 2
    src = body["sources"][0]
    assert src["document_id"] == real_doc_id
    assert src["filename"] == "test.pdf"  # resolved from DB
    assert src["page_number"] == 3
    assert src["relevance_score"] == pytest.approx(0.92)
    assert "chunk_text" in src


async def test_query_without_auth_returns_401_or_403(client: AsyncClient):
    """Request without Authorization header must be rejected."""
    resp = await client.post(
        QUERY_URL,
        json={"question": "What is RAG?"},
    )
    assert resp.status_code in (401, 403)


async def test_query_with_invalid_token_returns_401(client: AsyncClient):
    """A garbage Bearer token must be rejected with 401."""
    resp = await client.post(
        QUERY_URL,
        json={"question": "What is RAG?"},
        headers={"Authorization": "Bearer thisisnotalidtoken"},
    )
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# POST /api/rag/query — document_ids filter
# ---------------------------------------------------------------------------


async def test_query_with_document_ids_passes_filter_to_query_similar(client: AsyncClient):
    """Providing document_ids must build the correct Pinecone $in filter."""
    token = await _register_and_get_token(client)

    pe, pq, pa = _mock_rag_externals(chunks=[])
    with pe, pq as mock_query, pa:
        resp = await client.post(
            QUERY_URL,
            json={"question": "Tell me about invoices.", "document_ids": ["id1", "id2"]},
            headers=_auth_headers(token),
        )

    assert resp.status_code == 200, resp.text

    # Verify that query_similar received the $in filter.
    call_kwargs = mock_query.call_args[1]
    assert call_kwargs["filter"] == {"doc_id": {"$in": ["id1", "id2"]}}


async def test_query_without_document_ids_passes_none_filter(client: AsyncClient):
    """Omitting document_ids must pass filter=None to query_similar."""
    token = await _register_and_get_token(client)

    pe, pq, pa = _mock_rag_externals(chunks=[])
    with pe, pq as mock_query, pa:
        resp = await client.post(
            QUERY_URL,
            json={"question": "Tell me about invoices."},
            headers=_auth_headers(token),
        )

    assert resp.status_code == 200, resp.text
    call_kwargs = mock_query.call_args[1]
    assert call_kwargs["filter"] is None


# ---------------------------------------------------------------------------
# POST /api/rag/query — conversation memory
# ---------------------------------------------------------------------------


async def test_query_second_turn_uses_conversation_history(client: AsyncClient):
    """The second query in the same conversation prepends prior history."""
    token = await _register_and_get_token(client)

    pe, pq, pa = _mock_rag_externals(chunks=[], answer="First answer")
    with pe, pq, pa:
        first_resp = await client.post(
            QUERY_URL,
            json={"question": "What is RAG?"},
            headers=_auth_headers(token),
        )
    assert first_resp.status_code == 200, first_resp.text
    conversation_id = first_resp.json()["conversation_id"]

    # Second query — capture what generate_answer receives.
    pe2, pq2, pa2 = _mock_rag_externals(chunks=[], answer="Second answer")
    with pe2, pq2, pa2 as mock_answer:
        second_resp = await client.post(
            QUERY_URL,
            json={"question": "Can you elaborate?", "conversation_id": conversation_id},
            headers=_auth_headers(token),
        )

    assert second_resp.status_code == 200, second_resp.text

    # The question passed to generate_answer should contain prior history.
    called_question = mock_answer.call_args[0][0]
    assert "What is RAG?" in called_question
    assert "First answer" in called_question
    assert "Can you elaborate?" in called_question


async def test_query_assigns_new_conversation_id_when_not_provided(client: AsyncClient):
    """Each query without a conversation_id must receive a fresh UUID."""
    token = await _register_and_get_token(client)

    conversation_ids = []
    for _ in range(2):
        pe, pq, pa = _mock_rag_externals(chunks=[])
        with pe, pq, pa:
            resp = await client.post(
                QUERY_URL,
                json={"question": "Hello"},
                headers=_auth_headers(token),
            )
        assert resp.status_code == 200, resp.text
        conversation_ids.append(resp.json()["conversation_id"])

    assert conversation_ids[0] != conversation_ids[1]


async def test_query_reuses_provided_conversation_id(client: AsyncClient):
    """When a conversation_id is explicitly provided, it must appear in the response."""
    token = await _register_and_get_token(client)
    fixed_id = "fixed-conversation-id-123"

    pe, pq, pa = _mock_rag_externals(chunks=[])
    with pe, pq, pa:
        resp = await client.post(
            QUERY_URL,
            json={"question": "Hi", "conversation_id": fixed_id},
            headers=_auth_headers(token),
        )

    assert resp.status_code == 200, resp.text
    assert resp.json()["conversation_id"] == fixed_id


# ---------------------------------------------------------------------------
# POST /api/rag/query — empty chunks
# ---------------------------------------------------------------------------


async def test_query_with_empty_chunks_still_returns_answer(client: AsyncClient):
    """When no chunks are retrieved, the LLM handles the 'not found' case gracefully."""
    token = await _register_and_get_token(client)

    not_found_answer = "I couldn't find information about that in the documents"
    pe, pq, pa = _mock_rag_externals(chunks=[], answer=not_found_answer)
    with pe, pq, pa:
        resp = await client.post(
            QUERY_URL,
            json={"question": "What is the meaning of life?"},
            headers=_auth_headers(token),
        )

    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["answer"] == not_found_answer
    assert body["sources"] == []


# ---------------------------------------------------------------------------
# POST /api/rag/query — unknown doc_id falls back to doc_id as filename
# ---------------------------------------------------------------------------


async def test_query_unknown_doc_id_falls_back_to_doc_id_as_filename(client: AsyncClient):
    """If a chunk's doc_id is not in the DB, filename falls back to doc_id."""
    token = await _register_and_get_token(client)

    orphan_chunks = [
        {
            "id": "orphan_0",
            "score": 0.75,
            "text": "Orphan text.",
            "page": 1,
            "doc_id": "nonexistent-doc-id",
        }
    ]

    pe, pq, pa = _mock_rag_externals(chunks=orphan_chunks)
    with pe, pq, pa:
        resp = await client.post(
            QUERY_URL,
            json={"question": "Anything?"},
            headers=_auth_headers(token),
        )

    assert resp.status_code == 200, resp.text
    src = resp.json()["sources"][0]
    # filename must fall back to the doc_id string when no DB record exists
    assert src["filename"] == "nonexistent-doc-id"
    assert src["document_id"] == "nonexistent-doc-id"


# ---------------------------------------------------------------------------
# GET /api/rag/conversations/{id}
# ---------------------------------------------------------------------------


async def test_get_conversation_returns_history(client: AsyncClient):
    """After a query, the conversation history endpoint returns the stored turn."""
    token = await _register_and_get_token(client)

    pe, pq, pa = _mock_rag_externals(chunks=[], answer="My test answer")
    with pe, pq, pa:
        query_resp = await client.post(
            QUERY_URL,
            json={"question": "Test question?"},
            headers=_auth_headers(token),
        )

    assert query_resp.status_code == 200, query_resp.text
    conversation_id = query_resp.json()["conversation_id"]

    hist_resp = await client.get(f"/api/rag/conversations/{conversation_id}")

    assert hist_resp.status_code == 200, hist_resp.text
    body = hist_resp.json()
    assert body["conversation_id"] == conversation_id
    assert len(body["messages"]) == 1
    assert body["messages"][0]["question"] == "Test question?"
    assert body["messages"][0]["answer"] == "My test answer"
    assert "created_at" in body
    assert "updated_at" in body


async def test_get_conversation_unknown_id_returns_404(client: AsyncClient):
    """Requesting history for a non-existent conversation_id must return 404."""
    resp = await client.get("/api/rag/conversations/does-not-exist-at-all")
    assert resp.status_code == 404


async def test_get_conversation_accumulates_multiple_turns(client: AsyncClient):
    """Multiple queries on the same conversation_id must accumulate as turns."""
    token = await _register_and_get_token(client)
    conversation_id = "multi-turn-test"

    turns = [
        ("Question one?", "Answer one."),
        ("Question two?", "Answer two."),
    ]

    for question, answer in turns:
        pe, pq, pa = _mock_rag_externals(chunks=[], answer=answer)
        with pe, pq, pa:
            resp = await client.post(
                QUERY_URL,
                json={"question": question, "conversation_id": conversation_id},
                headers=_auth_headers(token),
            )
        assert resp.status_code == 200, resp.text

    hist_resp = await client.get(f"/api/rag/conversations/{conversation_id}")
    assert hist_resp.status_code == 200
    messages = hist_resp.json()["messages"]
    assert len(messages) == 2
    assert messages[0]["question"] == "Question one?"
    assert messages[1]["question"] == "Question two?"
