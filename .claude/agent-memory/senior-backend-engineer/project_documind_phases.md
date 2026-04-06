---
name: DocuMind Phase Status
description: Current implementation phase, completed work, and key architectural facts about DocuMind backend
type: project
---

Phase 4 (RAG Query Pipeline) is complete as of 2026-04-06. Phases 1, 2a, 2b, 2c, 3 done previously.

**Completed:**
- `backend/app/auth/jwt.py` — bcrypt hashing, JWT creation/validation, `get_current_user` dependency
- `backend/app/auth/routes.py` — `/register` (201), `/login` (200), `/me` (protected); uses async SQLAlchemy DB queries
- `backend/app/documents/parser.py` — PyMuPDF text extraction, returns list[{page, text}]
- `backend/app/documents/chunker.py` — RecursiveCharacterTextSplitter via `langchain_text_splitters`
- `backend/app/documents/embeddings.py` — `get_embeddings(texts)` using OpenAI text-embedding-3-small
- `backend/app/documents/routes.py` — upload/list/delete endpoints; persists to DB + Pinecone
- `backend/app/rag/retriever.py` — `get_or_create_index`, `upsert_chunks` (batches of 100), `query_similar`, `delete_document_vectors`; lazy init via `_get_index()`
- `backend/app/rag/chain.py` — `generate_answer(question, chunks)` async; uses `langchain_core.prompts.ChatPromptTemplate` and `langchain_core.output_parsers.StrOutputParser` (NOT `langchain.prompts` — that module doesn't exist in LangChain 1.x)
- `backend/app/rag/memory.py` — `ConversationMemory` class: sliding window (max_turns=5), TTL=30min; `memory` module singleton
- `backend/app/rag/routes.py` — `POST /api/rag/query` (auth required): embeds question, queries Pinecone, generates answer, resolves filenames from DB, stores turn in memory; `GET /api/rag/conversations/{id}` (no auth)
- `backend/app/database.py` — async SQLAlchemy engine, `get_db` dependency
- `backend/app/db_models.py` — `UserModel` and `DocumentModel`; String PKs (UUID as string)
- `backend/app/main.py` — rag_router registered at `/api/rag`
- `backend/tests/conftest.py` — per-test in-memory SQLite; `get_db` overridden via dependency_overrides

**Key architectural facts:**
- LangChain prompts: `from langchain_core.prompts import ChatPromptTemplate` (not `langchain.prompts`)
- LangChain output parsers: `from langchain_core.output_parsers import StrOutputParser`
- RAG route embeds the raw question (not history) for vector search; prepends history to question only for generate_answer
- Filename fallback: if chunk's doc_id has no DB record, filename = doc_id string
- conversation memory is in-process only (no DB persistence); expires after 30 min idle
- `generate_answer` is async — must be awaited; mocked with `AsyncMock` in tests
- Test mock targets: `app.rag.routes.get_embeddings`, `app.rag.routes.query_similar`, `app.rag.routes.generate_answer`
- DATABASE_URL defaults to `sqlite+aiosqlite:///./documind.db`
- `expire_on_commit=False` on AsyncSessionLocal required for async patterns

**Next phase:** Phase 5 — Rate Limiting, structured logging, frontend wiring, Docker polish.
