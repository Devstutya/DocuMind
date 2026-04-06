---
name: DocuMind Phase Status
description: Current implementation phase, completed work, and key architectural facts about DocuMind backend
type: project
---

Phase 3 (Pinecone Vector Storage) is complete as of 2026-04-06. Phases 1, 2a, 2b done previously.

**Completed:**
- `backend/app/auth/jwt.py` — bcrypt hashing, JWT creation/validation, `get_current_user` dependency
- `backend/app/auth/routes.py` — `/register` (201), `/login` (200), `/me` (protected) using in-memory dict `_users`
- `backend/app/documents/parser.py` — PyMuPDF text extraction, returns list[{page, text}]
- `backend/app/documents/chunker.py` — RecursiveCharacterTextSplitter via `langchain_text_splitters`
- `backend/app/documents/embeddings.py` — `get_embeddings(texts)` using OpenAI text-embedding-3-small
- `backend/app/documents/routes.py` — upload now calls `get_embeddings` then `upsert_chunks`; delete calls `delete_document_vectors` (best-effort, swallows errors); in-memory `_documents` dict
- `backend/app/rag/retriever.py` — `get_or_create_index`, `upsert_chunks` (batches of 100), `query_similar`, `delete_document_vectors`; Pinecone index is lazily initialized via `_get_index()` to avoid network call on import
- `backend/tests/test_routes/test_documents.py` — 14 tests all passing; all Pinecone/OpenAI calls mocked via `unittest.mock.patch`
- `backend/tests/test_rag/test_retriever.py` — 17 tests all passing; patches `_get_index` at function level with `patch.object`

**Key architectural facts:**
- Pinecone client `pc` is module-level but `get_or_create_index()` is called lazily through `_get_index()` — safe to import in tests with a fake key
- Text stored in Pinecone metadata is truncated to 1000 chars
- delete_document_vectors is best-effort in the route (exception is swallowed) so a Pinecone outage never blocks document deletion
- In-memory stores (`_users`, `_documents`) intentional; real DB deferred to a later phase
- langchain import: use `from langchain_text_splitters import RecursiveCharacterTextSplitter`

**Next phase:** Phase 4 — RAG Query Pipeline (rag/chain.py, rag/memory.py, rag/routes.py: POST /api/query endpoint).

**Why:** Pinecone retrieval is ready; Phase 4 builds the LangChain QA chain on top and adds conversation memory.

**How to apply:** Start from rag/chain.py (LangChain ChatOpenAI + prompt), then rag/memory.py (sliding window), then rag/routes.py (POST /api/query). Wire into main.py.
