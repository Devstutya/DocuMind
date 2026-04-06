# backend/app/rag/retriever.py
import os
from typing import Optional

from pinecone import Pinecone, ServerlessSpec
from app.config import settings

pc = Pinecone(api_key=settings.PINECONE_API_KEY)

# The index handle is initialised lazily on first use so that importing this
# module during testing (with a fake API key) does not trigger a real network
# call to Pinecone.
_index: Optional[object] = None


def _get_index():
    """Return the module-level Pinecone index handle, creating it if needed.

    Uses a module-level cache so the underlying HTTP connection is reused
    across calls within the same process lifetime.
    """
    global _index
    if _index is None:
        _index = get_or_create_index()
    return _index


def get_or_create_index(index_name: str = "documind"):
    """Get an existing Pinecone index or create it if absent.

    The index is configured for ``text-embedding-3-small`` vectors (1536
    dimensions, cosine similarity) hosted on AWS us-east-1 serverless.

    Args:
        index_name: Name of the Pinecone index. Defaults to ``"documind"``.

    Returns:
        A :class:`pinecone.Index` handle ready for upsert/query/delete calls.
    """
    existing_names = [idx.name for idx in pc.list_indexes()]
    if index_name not in existing_names:
        pc.create_index(
            name=index_name,
            dimension=1536,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )
    return pc.Index(index_name)


def upsert_chunks(chunks: list[dict], embeddings: list[list[float]]) -> None:
    """Upsert document chunks with their embeddings to Pinecone.

    Vectors are sent in batches of 100 to stay within Pinecone's recommended
    upsert batch size. Each vector stores its source text (truncated to 1000
    chars) and provenance metadata in Pinecone's metadata fields so that
    retrieved chunks can be rendered without a separate database lookup.

    Args:
        chunks: List of chunk dicts as returned by :func:`chunk_document`.
            Each dict must have ``"id"``, ``"text"``, and ``"metadata"`` keys.
        embeddings: List of float vectors in the same order as ``chunks``.
    """
    vectors = [
        {
            "id": chunk["id"],
            "values": embedding,
            "metadata": {
                **chunk["metadata"],
                "text": chunk["text"][:1000],
            },
        }
        for chunk, embedding in zip(chunks, embeddings)
    ]

    index = _get_index()
    for i in range(0, len(vectors), 100):
        index.upsert(vectors=vectors[i : i + 100])


def query_similar(
    query_embedding: list[float],
    top_k: int = 5,
    filter: dict | None = None,
) -> list[dict]:
    """Query Pinecone for the most semantically similar chunks.

    Args:
        query_embedding: 1536-dimensional float vector for the user's question.
        top_k: Number of nearest neighbours to return (default 5).
        filter: Optional Pinecone metadata filter dict, e.g.
            ``{"doc_id": {"$in": ["abc", "def"]}}``.

    Returns:
        List of result dicts, each with keys:
        ``id``, ``score``, ``text``, ``page``, ``doc_id``.

    Example::

        results = query_similar(embedding, top_k=3, filter={"doc_id": {"$eq": "abc"}})
        # [{"id": "abc_0", "score": 0.92, "text": "...", "page": 1, "doc_id": "abc"}, ...]
    """
    index = _get_index()
    results = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True,
        filter=filter,
    )
    return [
        {
            "id": match["id"],
            "score": match["score"],
            "text": match["metadata"].get("text", ""),
            "page": match["metadata"].get("page"),
            "doc_id": match["metadata"].get("doc_id"),
        }
        for match in results["matches"]
    ]


def delete_document_vectors(doc_id: str) -> None:
    """Delete all Pinecone vectors that belong to a document.

    Uses a metadata filter on the ``doc_id`` field so that every chunk
    created for this document is removed in a single call. This must be
    invoked whenever a document is deleted from the application to avoid
    orphaned vectors consuming index quota.

    Args:
        doc_id: The document identifier used when the chunks were upserted.
    """
    index = _get_index()
    index.delete(filter={"doc_id": {"$eq": doc_id}})
