# backend/app/rag/routes.py
"""RAG query endpoints.

Provides:
  POST /api/rag/query                      — Authenticated question-answering
  GET  /api/rag/conversations/{id}         — Retrieve conversation history
"""

import time
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import get_current_user
from app.config import settings
from app.database import get_db
from app.db_models import DocumentModel
from app.documents.embeddings import get_embeddings
from app.models import ConversationHistory, QueryRequest, QueryResponse, SourceCitation
from app.rag.chain import generate_answer
from app.rag.memory import memory
from app.rag.retriever import query_similar

router = APIRouter()


@router.post(
    "/query",
    response_model=QueryResponse,
    summary="Query documents using RAG",
    responses={
        200: {"description": "Answer generated with source citations"},
        401: {"description": "Missing or invalid token"},
    },
)
async def query_documents(
    request: QueryRequest,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> QueryResponse:
    """Answer a question by retrieving relevant document chunks and generating a response.

    Flow:
    1. Assigns a new UUID as ``conversation_id`` if one is not provided.
    2. Prepends prior conversation history to the question for follow-up
       awareness (sliding-window memory, up to 5 turns).
    3. Embeds the raw question with ``text-embedding-3-small``.
    4. Queries Pinecone for the top-K most similar chunks, optionally
       filtered to a specific set of document IDs.
    5. Calls GPT-4o-mini via LangChain to generate a cited answer.
    6. Stores the Q&A turn in memory and returns the response with timing.

    Args:
        request: Validated ``QueryRequest`` containing the question and
            optional ``document_ids`` / ``conversation_id``.
        current_user_id: JWT sub claim (injected by ``get_current_user``).
        db: Async database session (injected by ``get_db``).

    Returns:
        ``QueryResponse`` with the answer text, source citations (including
        filename resolved from the database), conversation ID, and wall-clock
        query time in milliseconds.

    Example request::

        POST /api/rag/query
        Authorization: Bearer <jwt>
        {
          "question": "What is the refund policy?",
          "document_ids": ["abc123"],
          "conversation_id": "optional-uuid"
        }

    Example response::

        {
          "answer": "The refund policy states... [Page 4]",
          "sources": [
            {
              "document_id": "abc123",
              "filename": "policy.pdf",
              "page_number": 4,
              "chunk_text": "Refunds are processed within...",
              "relevance_score": 0.92
            }
          ],
          "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
          "query_time_ms": 342.5
        }
    """
    start_time = time.time()

    # Assign a conversation ID if the caller did not supply one.
    conversation_id = request.conversation_id or str(uuid.uuid4())

    # Build a context-aware question by prepending conversation history.
    prior_history = memory.format_history(conversation_id)
    if prior_history:
        question_with_history = f"{prior_history}\nUser: {request.question}"
    else:
        question_with_history = request.question

    # Embed only the raw question (not the history) for vector search so the
    # semantic meaning of the current query is not diluted by prior turns.
    query_embedding = get_embeddings([request.question])[0]

    # Build an optional Pinecone metadata filter.
    pinecone_filter: dict | None = None
    if request.document_ids:
        pinecone_filter = {"doc_id": {"$in": request.document_ids}}

    # Retrieve similar chunks from Pinecone.
    chunks = query_similar(
        query_embedding,
        top_k=settings.TOP_K_RESULTS,
        filter=pinecone_filter,
    )

    # Generate the answer using the LangChain QA chain.
    answer = await generate_answer(question_with_history, chunks)

    # Resolve document filenames from the database and build source citations.
    sources: list[SourceCitation] = []
    for chunk in chunks:
        doc_id: str = chunk.get("doc_id") or ""
        filename = doc_id  # fallback if the DB record is missing

        if doc_id:
            doc_record = await db.scalar(
                select(DocumentModel).where(DocumentModel.id == doc_id)
            )
            if doc_record is not None:
                filename = doc_record.filename

        sources.append(
            SourceCitation(
                document_id=doc_id,
                filename=filename,
                page_number=chunk.get("page") or 0,
                chunk_text=chunk.get("text") or "",
                relevance_score=chunk.get("score") or 0.0,
            )
        )

    # Store the Q&A turn in memory for future follow-up questions.
    memory.add_turn(conversation_id, request.question, answer)

    query_time_ms = (time.time() - start_time) * 1000

    return QueryResponse(
        answer=answer,
        sources=sources,
        conversation_id=conversation_id,
        query_time_ms=query_time_ms,
    )


@router.get(
    "/conversations/{conversation_id}",
    response_model=ConversationHistory,
    summary="Retrieve conversation history",
    responses={
        200: {"description": "Conversation history for the given ID"},
        404: {"description": "Conversation not found or expired"},
    },
)
async def get_conversation(conversation_id: str) -> ConversationHistory:
    """Return the in-memory conversation history for a session.

    No authentication is required — conversation IDs are UUIDs that are
    effectively unguessable, so possession of the ID is treated as proof of
    access.

    Returns a 404 if the conversation has expired (30-minute TTL) or was
    never created.

    Args:
        conversation_id: UUID assigned at query time.

    Returns:
        ``ConversationHistory`` with the list of Q&A turn dicts.

    Example request::

        GET /api/rag/conversations/550e8400-e29b-41d4-a716-446655440000

    Example response::

        {
          "conversation_id": "550e8400-...",
          "messages": [
            {"question": "What is RAG?", "answer": "It stands for..."}
          ],
          "created_at": "2026-04-06T10:00:00",
          "updated_at": "2026-04-06T10:01:00"
        }
    """
    history = memory.get_history(conversation_id)
    if not history:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found or has expired.",
        )

    # Use the timestamp of the first and last turns for created_at / updated_at.
    created_at = history[0]["timestamp"]
    updated_at = history[-1]["timestamp"]

    return ConversationHistory(
        conversation_id=conversation_id,
        messages=[
            {"question": turn["question"], "answer": turn["answer"]}
            for turn in history
        ],
        created_at=created_at,
        updated_at=updated_at,
    )
