# backend/tests/test_rag/test_retriever.py
"""
Unit tests for app.rag.retriever.

The Pinecone client (``pc``) is instantiated at module load time but
``get_or_create_index`` is only called lazily through ``_get_index()``, so
no real network call is made on import.

Strategy: patch ``app.rag.retriever._get_index`` at the function level so
every public function that calls ``_get_index()`` receives our MagicMock
index instead of hitting Pinecone. This keeps the tests fully isolated.

Covers:
- upsert_chunks: correct vector construction, text truncation to 1000 chars,
  batching into groups of 100, empty input
- query_similar: Pinecone response mapped to expected dict format, filter
  forwarded, include_metadata always True, missing metadata fields
- delete_document_vectors: index.delete called with the correct $eq filter
"""

from unittest.mock import MagicMock, patch

import pytest

import app.rag.retriever as retriever_module


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_mock_index() -> MagicMock:
    """Return a fresh MagicMock that stands in for a pinecone.Index instance."""
    return MagicMock()


def _make_chunks(n: int, text_length: int = 50) -> list[dict]:
    """Create *n* minimal chunk dicts for testing."""
    return [
        {
            "id": f"doc_test_{i}",
            "text": "x" * text_length,
            "metadata": {"doc_id": "doc_test", "page": 1, "chunk_index": i},
        }
        for i in range(n)
    ]


def _make_embeddings(n: int, dim: int = 1536) -> list[list[float]]:
    """Create *n* zero-valued embedding vectors."""
    return [[0.0] * dim for _ in range(n)]


def _make_pinecone_match(
    match_id: str,
    score: float,
    text: str = "some text",
    page: int = 1,
    doc_id: str = "doc_abc",
) -> dict:
    """Build a minimal Pinecone query result match dict."""
    return {
        "id": match_id,
        "score": score,
        "metadata": {"text": text, "page": page, "doc_id": doc_id},
    }


# ---------------------------------------------------------------------------
# upsert_chunks tests
# ---------------------------------------------------------------------------


def test_upsert_chunks_single_batch():
    """Fewer than 100 chunks must trigger exactly one index.upsert call."""
    mock_index = _make_mock_index()
    with patch.object(retriever_module, "_get_index", return_value=mock_index):
        chunks = _make_chunks(3)
        embeddings = _make_embeddings(3)

        retriever_module.upsert_chunks(chunks, embeddings)

    assert mock_index.upsert.call_count == 1
    vectors = mock_index.upsert.call_args[1]["vectors"]
    assert len(vectors) == 3


def test_upsert_chunks_batches_at_100():
    """Exactly 100 chunks must still be sent in a single batch."""
    mock_index = _make_mock_index()
    with patch.object(retriever_module, "_get_index", return_value=mock_index):
        chunks = _make_chunks(100)
        embeddings = _make_embeddings(100)

        retriever_module.upsert_chunks(chunks, embeddings)

    assert mock_index.upsert.call_count == 1
    vectors = mock_index.upsert.call_args[1]["vectors"]
    assert len(vectors) == 100


def test_upsert_chunks_splits_into_multiple_batches():
    """250 chunks must be sent in 3 batches (100 + 100 + 50)."""
    mock_index = _make_mock_index()
    with patch.object(retriever_module, "_get_index", return_value=mock_index):
        chunks = _make_chunks(250)
        embeddings = _make_embeddings(250)

        retriever_module.upsert_chunks(chunks, embeddings)

    assert mock_index.upsert.call_count == 3
    calls = mock_index.upsert.call_args_list
    assert len(calls[0][1]["vectors"]) == 100
    assert len(calls[1][1]["vectors"]) == 100
    assert len(calls[2][1]["vectors"]) == 50


def test_upsert_chunks_truncates_text_to_1000_chars():
    """Text longer than 1000 characters must be truncated in stored metadata."""
    mock_index = _make_mock_index()
    long_text = "a" * 2000
    chunks = [
        {
            "id": "doc_trunc_0",
            "text": long_text,
            "metadata": {"doc_id": "doc_trunc", "page": 1, "chunk_index": 0},
        }
    ]
    embeddings = _make_embeddings(1)

    with patch.object(retriever_module, "_get_index", return_value=mock_index):
        retriever_module.upsert_chunks(chunks, embeddings)

    vectors = mock_index.upsert.call_args[1]["vectors"]
    stored_text = vectors[0]["metadata"]["text"]
    assert len(stored_text) == 1000
    assert stored_text == "a" * 1000


def test_upsert_chunks_preserves_short_text():
    """Text shorter than 1000 chars must not be modified."""
    mock_index = _make_mock_index()
    short_text = "hello world"
    chunks = [
        {
            "id": "doc_short_0",
            "text": short_text,
            "metadata": {"doc_id": "doc_short", "page": 2, "chunk_index": 0},
        }
    ]
    embeddings = _make_embeddings(1)

    with patch.object(retriever_module, "_get_index", return_value=mock_index):
        retriever_module.upsert_chunks(chunks, embeddings)

    vectors = mock_index.upsert.call_args[1]["vectors"]
    assert vectors[0]["metadata"]["text"] == short_text


def test_upsert_chunks_vector_structure():
    """Each vector must contain id, values, and metadata with text + provenance."""
    mock_index = _make_mock_index()
    chunks = _make_chunks(1, text_length=10)
    embeddings = [[0.1] * 1536]

    with patch.object(retriever_module, "_get_index", return_value=mock_index):
        retriever_module.upsert_chunks(chunks, embeddings)

    vectors = mock_index.upsert.call_args[1]["vectors"]
    v = vectors[0]
    assert v["id"] == "doc_test_0"
    assert v["values"] == [0.1] * 1536
    assert v["metadata"]["doc_id"] == "doc_test"
    assert v["metadata"]["page"] == 1
    assert v["metadata"]["chunk_index"] == 0
    assert "text" in v["metadata"]


def test_upsert_chunks_empty_list_makes_no_calls():
    """Passing empty lists must result in zero upsert calls."""
    mock_index = _make_mock_index()

    with patch.object(retriever_module, "_get_index", return_value=mock_index):
        retriever_module.upsert_chunks([], [])

    mock_index.upsert.assert_not_called()


# ---------------------------------------------------------------------------
# query_similar tests
# ---------------------------------------------------------------------------


def test_query_similar_maps_response_correctly():
    """query_similar must map Pinecone match dicts to the expected output format."""
    mock_index = _make_mock_index()
    mock_index.query.return_value = {
        "matches": [
            _make_pinecone_match("doc_abc_0", 0.95, text="First chunk", page=3, doc_id="doc_abc"),
            _make_pinecone_match("doc_abc_1", 0.88, text="Second chunk", page=4, doc_id="doc_abc"),
        ]
    }

    with patch.object(retriever_module, "_get_index", return_value=mock_index):
        results = retriever_module.query_similar([0.0] * 1536, top_k=2)

    assert len(results) == 2
    assert results[0] == {
        "id": "doc_abc_0",
        "score": 0.95,
        "text": "First chunk",
        "page": 3,
        "doc_id": "doc_abc",
    }
    assert results[1] == {
        "id": "doc_abc_1",
        "score": 0.88,
        "text": "Second chunk",
        "page": 4,
        "doc_id": "doc_abc",
    }


def test_query_similar_passes_top_k():
    """The top_k parameter must be forwarded to index.query."""
    mock_index = _make_mock_index()
    mock_index.query.return_value = {"matches": []}

    with patch.object(retriever_module, "_get_index", return_value=mock_index):
        retriever_module.query_similar([0.0] * 1536, top_k=7)

    call_kwargs = mock_index.query.call_args[1]
    assert call_kwargs["top_k"] == 7


def test_query_similar_passes_filter():
    """A non-None filter dict must be forwarded to index.query."""
    mock_index = _make_mock_index()
    mock_index.query.return_value = {"matches": []}
    filt = {"doc_id": {"$in": ["doc_x", "doc_y"]}}

    with patch.object(retriever_module, "_get_index", return_value=mock_index):
        retriever_module.query_similar([0.0] * 1536, top_k=5, filter=filt)

    call_kwargs = mock_index.query.call_args[1]
    assert call_kwargs["filter"] == filt


def test_query_similar_none_filter_passed_through():
    """When filter is None it must still be forwarded (Pinecone ignores None)."""
    mock_index = _make_mock_index()
    mock_index.query.return_value = {"matches": []}

    with patch.object(retriever_module, "_get_index", return_value=mock_index):
        retriever_module.query_similar([0.0] * 1536, filter=None)

    call_kwargs = mock_index.query.call_args[1]
    assert call_kwargs["filter"] is None


def test_query_similar_includes_metadata():
    """index.query must be called with include_metadata=True."""
    mock_index = _make_mock_index()
    mock_index.query.return_value = {"matches": []}

    with patch.object(retriever_module, "_get_index", return_value=mock_index):
        retriever_module.query_similar([0.0] * 1536)

    call_kwargs = mock_index.query.call_args[1]
    assert call_kwargs["include_metadata"] is True


def test_query_similar_missing_metadata_fields_default_to_none():
    """Matches with absent metadata fields must not raise — defaults to None/empty."""
    mock_index = _make_mock_index()
    mock_index.query.return_value = {
        "matches": [
            {"id": "bare_0", "score": 0.5, "metadata": {}},
        ]
    }

    with patch.object(retriever_module, "_get_index", return_value=mock_index):
        results = retriever_module.query_similar([0.0] * 1536)

    assert results[0]["text"] == ""
    assert results[0]["page"] is None
    assert results[0]["doc_id"] is None


def test_query_similar_empty_matches_returns_empty_list():
    """No matches must return an empty list without errors."""
    mock_index = _make_mock_index()
    mock_index.query.return_value = {"matches": []}

    with patch.object(retriever_module, "_get_index", return_value=mock_index):
        results = retriever_module.query_similar([0.0] * 1536)

    assert results == []


# ---------------------------------------------------------------------------
# delete_document_vectors tests
# ---------------------------------------------------------------------------


def test_delete_document_vectors_calls_index_delete():
    """delete_document_vectors must call index.delete with the correct filter."""
    mock_index = _make_mock_index()

    with patch.object(retriever_module, "_get_index", return_value=mock_index):
        retriever_module.delete_document_vectors("doc_xyz")

    mock_index.delete.assert_called_once_with(
        filter={"doc_id": {"$eq": "doc_xyz"}}
    )


def test_delete_document_vectors_uses_eq_operator():
    """The filter must use the $eq operator, not $in or any other variant."""
    mock_index = _make_mock_index()

    with patch.object(retriever_module, "_get_index", return_value=mock_index):
        retriever_module.delete_document_vectors("my_doc")

    filter_arg = mock_index.delete.call_args[1]["filter"]
    assert "$eq" in filter_arg["doc_id"]
    assert filter_arg["doc_id"]["$eq"] == "my_doc"


def test_delete_document_vectors_different_doc_ids():
    """Each call must use the doc_id that was passed in."""
    mock_index = _make_mock_index()

    with patch.object(retriever_module, "_get_index", return_value=mock_index):
        for doc_id in ("doc_a", "doc_b", "doc_c"):
            retriever_module.delete_document_vectors(doc_id)

    assert mock_index.delete.call_count == 3
    called_ids = [
        c[1]["filter"]["doc_id"]["$eq"]
        for c in mock_index.delete.call_args_list
    ]
    assert called_ids == ["doc_a", "doc_b", "doc_c"]
