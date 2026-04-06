# backend/app/documents/chunker.py
from langchain_text_splitters import RecursiveCharacterTextSplitter


def chunk_document(
    pages: list[dict],
    doc_id: str,
    chunk_size: int = 1000,
    overlap: int = 200,
) -> list[dict]:
    """Split document pages into overlapping chunks with full provenance metadata.

    Each page's text is split independently so that the ``page`` metadata field
    always reflects the true source page rather than being averaged across a
    multi-page merge.

    Args:
        pages: List of ``{"page": int, "text": str}`` dicts as returned by
            :func:`extract_text_from_pdf`.
        doc_id: Unique document identifier used to build stable chunk IDs of
            the form ``<doc_id>_<chunk_index>``.
        chunk_size: Maximum number of characters per chunk (default 1000).
        overlap: Number of characters shared between adjacent chunks (default 200).

    Returns:
        List of chunk dicts, each containing:
        - ``id``: stable unique identifier string
        - ``text``: chunk content
        - ``metadata``: dict with ``doc_id``, ``page``, and ``chunk_index``

    Example::

        chunks = chunk_document(pages, doc_id="abc-123")
        # [{"id": "abc-123_0", "text": "...", "metadata": {"doc_id": "abc-123", "page": 1, "chunk_index": 0}}, ...]
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks: list[dict] = []
    chunk_index = 0

    for page_data in pages:
        page_chunks: list[str] = splitter.split_text(page_data["text"])
        for chunk_text in page_chunks:
            chunks.append(
                {
                    "id": f"{doc_id}_{chunk_index}",
                    "text": chunk_text,
                    "metadata": {
                        "doc_id": doc_id,
                        "page": page_data["page"],
                        "chunk_index": chunk_index,
                    },
                }
            )
            chunk_index += 1

    return chunks
