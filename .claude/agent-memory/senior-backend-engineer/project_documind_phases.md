---
name: DocuMind Phase Status
description: Current implementation phase, completed work, and key architectural facts about DocuMind backend
type: project
---

Phase 2c (SQLite DB persistence) is complete as of 2026-04-06. Phases 1, 2a, 2b, 3 done previously.

**Completed:**
- `backend/app/auth/jwt.py` — bcrypt hashing, JWT creation/validation, `get_current_user` dependency
- `backend/app/auth/routes.py` — `/register` (201), `/login` (200), `/me` (protected); uses async SQLAlchemy DB queries (no more _users dict)
- `backend/app/documents/parser.py` — PyMuPDF text extraction, returns list[{page, text}]
- `backend/app/documents/chunker.py` — RecursiveCharacterTextSplitter via `langchain_text_splitters`
- `backend/app/documents/embeddings.py` — `get_embeddings(texts)` using OpenAI text-embedding-3-small
- `backend/app/documents/routes.py` — upload calls `get_embeddings` then `upsert_chunks`, persists to DB; delete removes from Pinecone (best-effort) + DB; list queries DB by user_id
- `backend/app/rag/retriever.py` — `get_or_create_index`, `upsert_chunks` (batches of 100), `query_similar`, `delete_document_vectors`; lazy init via `_get_index()`
- `backend/app/database.py` — `create_async_engine`, `AsyncSessionLocal` (expire_on_commit=False), `Base`, `get_db` FastAPI dependency
- `backend/app/db_models.py` — `UserModel` (table: users) and `DocumentModel` (table: documents); String PKs (UUID as string, SQLite-compatible)
- `backend/alembic/` — async Alembic env.py reading DATABASE_URL from settings; initial migration `0001_create_users_and_documents`
- `backend/app/main.py` — lifespan startup calls `Base.metadata.create_all` (dev convenience; use `alembic upgrade head` in prod)
- `backend/tests/conftest.py` — per-test in-memory SQLite (`sqlite+aiosqlite:///:memory:`); `get_db` overridden via `fastapi_app.dependency_overrides`; no shared state between tests

**Key architectural facts:**
- DATABASE_URL defaults to `sqlite+aiosqlite:///./documind.db`; override with env var for test isolation
- `expire_on_commit=False` on AsyncSessionLocal is critical for async patterns (avoids lazy-load errors after commit)
- DocumentModel.created_at maps to Pydantic's `uploaded_at` field in the DocumentMetadata response
- DocumentModel.id maps to Pydantic's `document_id` field
- Pinecone client `pc` is module-level but `get_or_create_index()` is called lazily through `_get_index()` — safe to import in tests with a fake key
- delete_document_vectors is best-effort in the route (exception is swallowed) so a Pinecone outage never blocks document deletion
- langchain import: use `from langchain_text_splitters import RecursiveCharacterTextSplitter`
- conftest imports the FastAPI app as `fastapi_app` (not `app`) to avoid name collision with the `app` package

**Next phase:** Phase 4 — RAG Query Pipeline (rag/chain.py, rag/memory.py, rag/routes.py: POST /api/query endpoint).

**Why:** DB persistence is in place; Phase 4 builds the LangChain QA chain on top of the Pinecone retrieval layer and adds conversation memory.

**How to apply:** Start from rag/chain.py (LangChain ChatOpenAI + prompt), then rag/memory.py (sliding window), then rag/routes.py (POST /api/query). Wire into main.py.
