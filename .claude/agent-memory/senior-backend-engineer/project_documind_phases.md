---
name: DocuMind Phase Status
description: Current implementation phase, completed work, and key architectural facts about DocuMind backend
type: project
---

Phase 2b (PDF Upload & Processing) is complete as of 2026-04-06. Phases 1 and 2a done previously.

**Completed:**
- `backend/app/auth/jwt.py` — bcrypt hashing, JWT creation/validation, `get_current_user` dependency
- `backend/app/auth/routes.py` — `/register` (201), `/login` (200), `/me` (protected) using in-memory dict `_users`
- `backend/app/documents/parser.py` — PyMuPDF text extraction, returns list[{page, text}]
- `backend/app/documents/chunker.py` — RecursiveCharacterTextSplitter via `langchain_text_splitters` (NOT `langchain.text_splitter` — moved package in langchain 1.x)
- `backend/app/documents/embeddings.py` — OpenAI embeddings stub (not called yet; Phase 3)
- `backend/app/documents/routes.py` — `/upload` (201), `/` list (200), `/{id}` delete (204); in-memory `_documents` dict; embedding/Pinecone skipped until Phase 3
- `backend/app/main.py` — documents router wired at `/api/documents`
- `backend/tests/conftest.py` — updated to also clear `_documents` and redirect `UPLOAD_DIR` to `tmp_path` per test
- `backend/tests/test_routes/test_documents.py` — 12 tests, all passing (25 total in suite)

**Key architectural facts:**
- In-memory stores (`_users`, `_documents`) are intentional for now; database deferred to a later phase
- Upload validation: content-type must be `application/pdf`; size checked against `MAX_FILE_SIZE_MB` after full read
- Files stored as `<doc_id>.pdf` under `UPLOAD_DIR` to avoid filename collisions
- langchain import: use `from langchain_text_splitters import RecursiveCharacterTextSplitter`

**Next phase:** Phase 3 — Pinecone vector storage (rag/retriever.py: upsert chunks after upload, delete on document delete).

**Why:** Embeddings are generated in Phase 2b's embeddings.py but not called; Phase 3 wires them into the upload flow.

**How to apply:** When continuing, start from Phase 3. The upload route already has a clear "skip embedding" comment where the Pinecone upsert call should go.
