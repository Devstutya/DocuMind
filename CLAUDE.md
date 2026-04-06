# DocuMind — RAG Knowledge Assistant
## Comprehensive Project Guide & Implementation Context

---

## Project Overview

DocuMind is an AI-powered document Q&A system using Retrieval-Augmented Generation (RAG). Users upload PDFs and ask questions, receiving answers with contextual citations. The system supports both demo mode (no auth) and full authenticated access with document management, conversation history, and personalized settings.

**Key Capabilities:**
- Semantic search across 500+ PDFs with page-level citations
- Sub-second query latency (<1s target)
- Conversation memory with sliding window context (5-turn memory)
- Demo mode for instant testing without authentication
- Full dashboard with document management and chat history

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| Frontend | React + Vite | Modern, fast dev experience |
| UI Framework | Tailwind CSS | Utility-first styling |
| Backend | FastAPI (Python 3.11+) | Async API server |
| LLM Framework | LangChain | RAG orchestration |
| LLM | OpenAI GPT-4o-mini | Cost-effective reasoning |
| Embeddings | text-embedding-3-small | 1536-dim vectors |
| Vector DB | Pinecone (serverless) | Semantic search |
| Relational DB | SQLite (dev) / PostgreSQL (prod) | User and document persistence |
| ORM | SQLAlchemy 2.0 async + Alembic | Database access and migrations |
| PDF Processing | PyMuPDF (fitz) | Text extraction |
| Auth | JWT + passlib/bcrypt | Secure authentication |
| Containerization | Docker + Compose | Production deployment |

---

## Current Status

### ✅ Completed (Phase 1)

**Project Structure:**
- [x] Backend directory structure (app/, auth/, documents/, rag/, utils/)
- [x] Frontend directory structure (components/, pages/, services/)
- [x] All __init__.py files and module setup

**Backend Foundation:**
- [x] FastAPI app with CORS middleware ([main.py](backend/app/main.py))
- [x] Configuration management with Pydantic Settings ([config.py](backend/app/config.py))
- [x] Pydantic models for Auth, Documents, RAG ([models.py](backend/app/models.py))
- [x] Health check endpoint (`/api/health`)

**Frontend Foundation:**
- [x] React + Vite setup with Tailwind CSS
- [x] Landing page with dual-path navigation (Demo vs Full Access)
- [x] Dashboard with sidebar navigation
- [x] Components: ChatInterface, DocumentUpload, SourceCitation, Sidebar
- [x] Pages: Home, Login, Dashboard with multiple sections (chat, documents, history, upload, settings, profile)
- [x] Routing configured between all pages

**Infrastructure:**
- [x] Docker configuration (backend & frontend Dockerfiles)
- [x] docker-compose.yml for orchestration
- [x] .env.example template with all required variables
- [x] .gitignore files for backend and frontend
- [x] README.md with setup instructions

**Environment Setup:**
- [x] Obtain OpenAI API key from [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
- [x] Obtain Pinecone API key and create index ("documind", 1536 dimensions, cosine metric)
- [x] Generate JWT secret key with `openssl rand -hex 32`
- [x] Create .env file with all credentials
- [x] Test backend startup: `uvicorn app.main:app --reload` ✅ **BACKEND RUNNING**

### ✅ Completed (Phase 2a) — Authentication System

- [x] `auth/jwt.py` — password hashing (bcrypt), JWT creation/validation, `get_current_user` dependency
- [x] `auth/routes.py` — `POST /api/auth/register`, `POST /api/auth/login`, `GET /api/auth/me`
- [x] In-memory user store (to be replaced with DB in a later phase)
- [x] Tests: 13/13 passing (`tests/test_routes/test_auth.py`)

### ✅ Completed (Phase 2b) — PDF Upload & Processing

- [x] `documents/parser.py` — PyMuPDF text extraction, page-by-page, skips blank pages
- [x] `documents/chunker.py` — `RecursiveCharacterTextSplitter` (1000 chars, 200 overlap), per-page chunking
- [x] `documents/embeddings.py` — OpenAI `text-embedding-3-small` wrapper (stubbed in upload until Phase 3)
- [x] `documents/routes.py` — `POST /api/documents/upload`, `GET /api/documents/`, `DELETE /api/documents/{id}`
- [x] In-memory document store (replaced by SQLite in Phase 2c)
- [x] Tests: 25/25 passing (`tests/test_routes/test_documents.py`)

### ✅ Completed (Phase 2c) — SQLite Database Persistence

- [x] `app/database.py` — async SQLAlchemy engine, `AsyncSessionLocal`, `Base`, `get_db` dependency
- [x] `app/db_models.py` — `UserModel` (table: `users`) and `DocumentModel` (table: `documents`) ORM models
- [x] `alembic/` — Alembic infrastructure with async env.py; initial migration `0001_create_users_and_documents`
- [x] `auth/routes.py` — replaced `_users` dict with `select(UserModel)` + `db.add` / `db.commit`
- [x] `documents/routes.py` — replaced `_documents` dict with `select(DocumentModel)` + DB CRUD
- [x] `app/main.py` — lifespan startup creates tables via `Base.metadata.create_all` (dev convenience)
- [x] `tests/conftest.py` — per-test in-memory SQLite engine, `get_db` dependency override, no shared state
- [x] Tests: 44/44 passing

### ✅ Completed (Phase 3) — Pinecone Vector Storage

- [x] `rag/retriever.py` — lazy Pinecone index init, `upsert_chunks` (batched 100), `query_similar`, `delete_document_vectors`
- [x] `documents/routes.py` — upload now generates embeddings + upserts to Pinecone; delete removes vectors
- [x] Upload failure is clean — disk file removed on embedding/Pinecone error, returns 500
- [x] Pinecone failure on delete is swallowed — outage can't permanently block deletion
- [x] Tests: 44/44 passing (`tests/test_routes/test_documents.py` + `tests/test_rag/test_retriever.py`)

### ✅ Completed (Phase 4) — RAG Query Pipeline

- [x] `rag/chain.py` — `generate_answer()` async LangChain chain with GPT-4o-mini (`langchain_core` imports)
- [x] `rag/chain.py` — `ChatOpenAI` lazy-initialized via `_get_llm()` to avoid module-level import crash when `OPENAI_API_KEY` not yet loaded
- [x] `rag/memory.py` — `ConversationMemory` singleton, 5-turn sliding window, 30min TTL expiry
- [x] `rag/routes.py` — `POST /api/rag/query` (auth required), `GET /api/rag/conversations/{id}`
- [x] History injected into LLM prompt only (not vector query — would dilute retrieval signal)
- [x] Filename falls back to `doc_id` if document deleted after upload
- [x] `main.py` — RAG router wired at `/api/rag`
- [x] Tests: 57/57 passing (`tests/test_rag/test_routes.py`)

### ✅ Completed (Phase 5) — Rate Limiting & Polish

- [x] `utils/rate_limit.py` — `RateLimiter` sliding-window class (per-user, 60s window); `require_rate_limit` FastAPI dependency wraps `get_current_user` — single `Depends` gives both auth + rate limiting
- [x] `rag/routes.py` — `POST /api/rag/query` now uses `require_rate_limit` instead of bare `get_current_user`; structured log lines emitted on query received and completed (includes `user_id`, `query_time_ms`, `sources_count`)
- [x] `utils/logging.py` — `_JsonFormatter` emits single-line JSON (`timestamp`, `level`, `logger`, `message` + any `extra` fields); `setup_logging()` called in FastAPI lifespan; `get_logger(__name__)` convenience wrapper
- [x] `main.py` — `setup_logging()` called at lifespan startup before tables are created
- [x] Frontend — `ChatInterface.jsx` already wired to `POST /api/rag/query` with conversation memory, source citations, and loading/error states
- [x] Tests: 62/62 passing (`tests/test_utils/test_rate_limit.py`)

---

## Project Structure

```
documind/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI entry point [DONE]
│   │   ├── config.py            # Settings & env vars [DONE]
│   │   ├── models.py            # Pydantic schemas [DONE]
│   │   ├── database.py          # Async SQLAlchemy engine, Base, get_db [DONE]
│   │   ├── db_models.py         # UserModel, DocumentModel ORM models [DONE]
│   │   ├── auth/
│   │   │   ├── __init__.py
│   │   │   ├── jwt.py           # Token creation/validation [DONE]
│   │   │   └── routes.py        # Login/register/me endpoints [DONE]
│   │   ├── demo/
│   │   │   ├── __init__.py
│   │   │   └── routes.py        # Unauthenticated demo upload [DONE]
│   │   ├── documents/
│   │   │   ├── __init__.py
│   │   │   ├── parser.py        # PDF text extraction [DONE]
│   │   │   ├── chunker.py       # Text chunking [DONE]
│   │   │   ├── embeddings.py    # OpenAI embedding calls [DONE]
│   │   │   └── routes.py        # Upload/list/delete endpoints [DONE]
│   │   ├── rag/
│   │   │   ├── __init__.py
│   │   │   ├── retriever.py     # Pinecone query logic [DONE]
│   │   │   ├── chain.py         # LangChain QA chain [DONE]
│   │   │   ├── memory.py        # Conversation memory [DONE]
│   │   │   └── routes.py        # Query endpoint [DONE]
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── logging.py       # Structured JSON logging [DONE]
│   │       └── rate_limit.py    # Rate limiting [DONE]
│   ├── alembic/                 # Migrations [DONE]
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   └── versions/
│   │       └── 0001_create_users_and_documents.py
│   ├── alembic.ini              [DONE]
│   ├── requirements.txt         [DONE]
│   ├── Dockerfile               [DONE]
│   └── .env.example             [DONE]
├── frontend/                    [COMPLETE]
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatInterface.jsx      [CREATED]
│   │   │   ├── DocumentUpload.jsx     [CREATED]
│   │   │   ├── SourceCitation.jsx     [CREATED]
│   │   │   └── Sidebar.jsx            [CREATED]
│   │   ├── pages/
│   │   │   ├── Home.jsx               [CREATED - Landing page]
│   │   │   ├── Login.jsx              [CREATED - Auth page]
│   │   │   └── Dashboard.jsx          [CREATED - Full dashboard]
│   │   ├── services/
│   │   │   └── api.js                 [CREATED]
│   │   ├── App.jsx                    [CREATED - Routing]
│   │   └── main.jsx                   [CREATED]
│   ├── package.json             [CREATED]
│   ├── Dockerfile               [CREATED]
│   └── tailwind.config.js       [CREATED]
├── docker-compose.yml           [CREATED]
├── .env.example                 [CREATED]
├── CLAUDE.md                    [THIS FILE]
└── README.md                    [CREATED]
```

---

## User Flow Architecture

### Demo Mode vs. Full Access

**Path 1: Demo Mode (No Authentication)**
```
Landing Page → "Try a Demo" → DemoPage
- Immediate PDF upload and chat
- No account required
- Data not persisted
- "Get Started" button to upgrade to full access
```

**Path 2: Full Access (Authentication Required)**
```
Landing Page → "Get Started" → Login/Register → Dashboard
- Full sidebar navigation
- Document management
- Chat history persistence
- Settings & profile
- Usage statistics
```

**Dashboard Features (Sidebar Navigation):**
- **Chat**: Main Q&A interface with document selector
- **My Documents**: View/manage uploaded PDFs
- **Chat History**: Browse previous conversations
- **Upload**: Dedicated document upload interface
- **Settings**: AI model selection, retrieval config, feature toggles
- **Profile**: User info, usage statistics (documents, queries)

---

## Implementation Phases

### Phase 2a: Authentication System

**Tasks:**
1. Implement user registration endpoint (`POST /api/auth/register`)
2. Implement login endpoint (`POST /api/auth/login`)
3. Implement JWT token generation and validation
4. Add password hashing with bcrypt
5. Create protected route decorator
6. Add user authentication to frontend (Login.jsx)

**Key Implementation - JWT Auth (`backend/app/auth/jwt.py`):**
```python
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

---

### Phase 2b: PDF Upload & Processing

**Tasks:**
1. Implement PDF upload endpoint (`POST /api/documents/upload`)
2. Add PyMuPDF text extraction (documents/parser.py)
3. Implement text chunking with RecursiveCharacterTextSplitter
4. Connect to Pinecone and create vector store
5. Generate embeddings with OpenAI
6. Store chunks in Pinecone with metadata

**Key Implementation - PDF Parser (`backend/app/documents/parser.py`):**
```python
import fitz  # PyMuPDF

def extract_text_from_pdf(file_path: str) -> list[dict]:
    """Extract text from PDF, returning list of {page, text} dicts."""
    doc = fitz.open(file_path)
    pages = []
    for page_num, page in enumerate(doc, 1):
        text = page.get_text("text")
        if text.strip():
            pages.append({
                "page": page_num,
                "text": text.strip()
            })
    doc.close()
    return pages
```

**Key Implementation - Chunker (`backend/app/documents/chunker.py`):**
```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

def chunk_document(pages: list[dict], doc_id: str, chunk_size: int = 1000, overlap: int = 200) -> list[dict]:
    """Split document pages into overlapping chunks with metadata."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        separators=["\n\n", "\n", ". ", " ", ""]
    )

    chunks = []
    chunk_index = 0

    for page_data in pages:
        page_chunks = splitter.split_text(page_data["text"])
        for chunk_text in page_chunks:
            chunks.append({
                "id": f"{doc_id}_{chunk_index}",
                "text": chunk_text,
                "metadata": {
                    "doc_id": doc_id,
                    "page": page_data["page"],
                    "chunk_index": chunk_index
                }
            })
            chunk_index += 1

    return chunks
```

**Key Implementation - Embeddings (`backend/app/documents/embeddings.py`):**
```python
from openai import OpenAI

client = OpenAI()

def get_embeddings(texts: list[str], model: str = "text-embedding-3-small") -> list[list[float]]:
    """Generate embeddings for a batch of texts."""
    response = client.embeddings.create(
        input=texts,
        model=model
    )
    return [item.embedding for item in response.data]
```

---

### Phase 3: Pinecone Vector Storage

**Tasks:**
1. Create Pinecone index (1536 dimensions, cosine metric)
2. Implement batch upsert for document chunks
3. Implement similarity search with metadata filtering
4. Add document deletion by doc_id

**Key Implementation - Pinecone Setup (`backend/app/rag/retriever.py`):**
```python
from pinecone import Pinecone, ServerlessSpec
import os

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

def create_index(index_name: str = "documind"):
    """Create Pinecone index if it doesn't exist."""
    if index_name not in pc.list_indexes().names():
        pc.create_index(
            name=index_name,
            dimension=1536,  # text-embedding-3-small dimension
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )
    return pc.Index(index_name)

index = create_index()

def upsert_chunks(chunks: list[dict], embeddings: list[list[float]]):
    """Upsert chunks with embeddings to Pinecone."""
    vectors = [
        {
            "id": chunk["id"],
            "values": embedding,
            "metadata": {
                **chunk["metadata"],
                "text": chunk["text"][:1000]  # Store text in metadata
            }
        }
        for chunk, embedding in zip(chunks, embeddings)
    ]

    # Batch upsert (100 vectors at a time)
    for i in range(0, len(vectors), 100):
        batch = vectors[i:i+100]
        index.upsert(vectors=batch)

def query_similar(query_embedding: list[float], top_k: int = 5, filter: dict = None) -> list[dict]:
    """Query Pinecone for similar chunks."""
    results = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True,
        filter=filter
    )
    return [
        {
            "id": match["id"],
            "score": match["score"],
            "text": match["metadata"].get("text", ""),
            "page": match["metadata"].get("page"),
            "doc_id": match["metadata"].get("doc_id")
        }
        for match in results["matches"]
    ]

def delete_document(doc_id: str):
    """Delete all chunks for a document."""
    index.delete(filter={"doc_id": {"$eq": doc_id}})
```

---

### Phase 4: RAG Query Pipeline

**Tasks:**
1. Implement query endpoint (`POST /api/query`)
2. Create vector retriever
3. Build RAG chain with LangChain
4. Add source citation extraction
5. Implement conversation memory
6. Connect ChatInterface to query endpoint

**Key Implementation - RAG Chain (`backend/app/rag/chain.py`):**
```python
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

SYSTEM_PROMPT = """You are a helpful assistant that answers questions based on the provided context.

Instructions:
- Answer based ONLY on the provided context
- If the context doesn't contain the answer, say "I couldn't find information about that in the documents"
- Cite your sources using [Page X] format
- Be concise but thorough

Context:
{context}"""

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "{question}")
])

def format_context(chunks: list[dict]) -> str:
    """Format retrieved chunks into context string."""
    context_parts = []
    for chunk in chunks:
        source = f"[Page {chunk['page']}]" if chunk.get('page') else ""
        context_parts.append(f"{source}\n{chunk['text']}")
    return "\n\n---\n\n".join(context_parts)

def create_rag_chain():
    """Create RAG chain with retriever."""

    def retrieve_and_format(question: str) -> dict:
        from app.documents.embeddings import get_embeddings
        from app.rag.retriever import query_similar

        # Get query embedding
        query_embedding = get_embeddings([question])[0]
        # Retrieve similar chunks
        chunks = query_similar(query_embedding, top_k=5)
        # Format context
        context = format_context(chunks)
        return {"context": context, "question": question, "sources": chunks}

    chain = (
        RunnablePassthrough()
        | retrieve_and_format
        | prompt
        | llm
        | StrOutputParser()
    )

    return chain
```

**Key Implementation - Conversation Memory (`backend/app/rag/memory.py`):**
```python
from collections import defaultdict
from datetime import datetime, timedelta

class ConversationMemory:
    def __init__(self, max_turns: int = 5, ttl_minutes: int = 30):
        self.conversations = defaultdict(list)
        self.max_turns = max_turns
        self.ttl = timedelta(minutes=ttl_minutes)
        self.last_access = {}

    def add_turn(self, conversation_id: str, question: str, answer: str):
        """Add a Q&A turn to conversation history."""
        self.conversations[conversation_id].append({
            "question": question,
            "answer": answer,
            "timestamp": datetime.now()
        })
        # Keep only last N turns (sliding window)
        if len(self.conversations[conversation_id]) > self.max_turns:
            self.conversations[conversation_id] = self.conversations[conversation_id][-self.max_turns:]
        self.last_access[conversation_id] = datetime.now()

    def get_history(self, conversation_id: str) -> list[dict]:
        """Get conversation history for context."""
        self._cleanup_expired()
        return self.conversations.get(conversation_id, [])

    def format_history(self, conversation_id: str) -> str:
        """Format history for prompt injection."""
        history = self.get_history(conversation_id)
        if not history:
            return ""

        formatted = []
        for turn in history:
            formatted.append(f"User: {turn['question']}")
            formatted.append(f"Assistant: {turn['answer']}")
        return "\n".join(formatted)

    def _cleanup_expired(self):
        """Remove expired conversations."""
        now = datetime.now()
        expired = [
            cid for cid, last in self.last_access.items()
            if now - last > self.ttl
        ]
        for cid in expired:
            del self.conversations[cid]
            del self.last_access[cid]

memory = ConversationMemory()
```

---

### Phase 5: Rate Limiting & Polish

**Tasks:**
1. Add rate limiting middleware (20 requests/minute per user)
2. Implement document management endpoints (list, delete)
3. Add conversation history persistence
4. Add error handling and logging
5. Write unit tests
6. Polish frontend UI/UX

**Key Implementation - Rate Limiting (`backend/app/utils/rate_limit.py`):**
```python
from fastapi import HTTPException
from collections import defaultdict
from datetime import datetime, timedelta

class RateLimiter:
    def __init__(self, requests_per_minute: int = 20):
        self.requests_per_minute = requests_per_minute
        self.requests = defaultdict(list)

    def check(self, user_id: str):
        now = datetime.now()
        minute_ago = now - timedelta(minutes=1)

        # Clean old requests
        self.requests[user_id] = [
            t for t in self.requests[user_id] if t > minute_ago
        ]

        if len(self.requests[user_id]) >= self.requests_per_minute:
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please wait a moment."
            )

        self.requests[user_id].append(now)

rate_limiter = RateLimiter()
```

---

## Environment Variables

Create a `.env` file in the project root:

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key-here

# Pinecone Configuration
PINECONE_API_KEY=your-pinecone-api-key-here
PINECONE_INDEX_NAME=documind
PINECONE_ENVIRONMENT=us-east-1

# JWT Security
# Generate with: openssl rand -hex 32
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# File Upload Settings
UPLOAD_DIR=./uploads
MAX_FILE_SIZE_MB=50

# CORS Settings
ALLOWED_ORIGINS=["http://localhost:5173","http://localhost:3000"]

# RAG Configuration
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K_RESULTS=5
MEMORY_WINDOW_SIZE=5

# Rate Limiting
RATE_LIMIT_PER_MINUTE=20
```

---

## Commands

### Backend Setup & Run
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Setup & Run
```bash
cd frontend
npm install
npm run dev
```

### Docker Deployment
```bash
# Full stack
docker-compose up --build

# Backend only
docker-compose up backend

# Frontend only
docker-compose up frontend
```

---

## Performance Targets

Track these metrics as we build:
- **Answer relevance**: 90%+ on evaluation benchmarks
- **Query latency**: <1 second (target: <500ms)
- **Vector search**: <200ms for similarity search
- **Document capacity**: 500+ PDFs (100K vectors on Pinecone free tier)
- **Follow-up reduction**: 35% fewer follow-up queries with conversation memory

---

## Testing & Evaluation

### Manual Testing Checklist
- [ ] Upload 5+ different PDFs (varying lengths, formats)
- [ ] Query with questions that span multiple documents
- [ ] Test follow-up questions ("What else?", "Can you elaborate?")
- [ ] Verify citations point to correct pages
- [ ] Test rate limiting by rapid requests
- [ ] Test with large files (>10MB PDFs)
- [ ] Test demo mode (no auth)
- [ ] Test full access mode (with auth)
- [ ] Verify conversation memory works across sessions

### Evaluation Script Example
```python
def evaluate_relevance(questions: list, expected_answers: list):
    """Manually evaluate answer relevance."""
    scores = []
    for q, expected in zip(questions, expected_answers):
        response = query_endpoint(q)
        # Score 0-1 based on how well answer matches expected
        score = manual_score(response.answer, expected)
        scores.append(score)
    return sum(scores) / len(scores)
```

---

## Code Style Guidelines

- **Python**: Use type hints, async/await for I/O operations
- **Functions**: Keep small and focused (single responsibility)
- **Docstrings**: Add to all public functions
- **Validation**: Use Pydantic models for request/response
- **Frontend**: Functional components with hooks
- **Error Handling**: Always return meaningful error messages
- **Logging**: Use structured logging (JSON format)

---

## Key Features Summary

1. **PDF Upload & Processing**: Extract text with PyMuPDF, chunk with RecursiveCharacterTextSplitter (1000 chars, 200 overlap)
2. **Vector Storage**: Embed chunks with OpenAI, store in Pinecone with metadata (doc_id, page, chunk_index)
3. **RAG Query Pipeline**: Retrieve top-5 similar chunks, inject into prompt, generate answer with citations
4. **Conversation Memory**: Sliding window (last 5 turns) for follow-up questions
5. **Source Citations**: Return page numbers and snippets with each answer
6. **Auth**: JWT tokens, bcrypt password hashing
7. **Rate Limiting**: 20 requests/minute per user
8. **Docker Deployment**: Multi-container setup with Docker Compose
9. **Demo Mode**: Try before you sign up (no authentication required)
10. **Dashboard**: Full-featured UI with sidebar navigation

---

## Notes

- Pinecone free tier: 1 index, 100K vectors — enough for 500+ docs
- Use GPT-4o-mini for cost efficiency during development
- Chunk text stored in Pinecone metadata (truncated to 1000 chars)
- All API routes under `/api/` prefix
- Frontend uses React Router for navigation
- Conversation memory expires after 30 minutes of inactivity
- Rate limiting applies per user_id (JWT sub claim)
- Docker volumes used for persistent uploads storage

---

## Next Immediate Actions

**🎉 All Phases Complete! (62/62 tests passing)**
- ✅ Phases 1–5 fully implemented
- ✅ Backend running at http://localhost:8000
- ✅ Swagger docs available at http://localhost:8000/docs

**Ready for Production / Docker Deployment:**

1. **End-to-end smoke test**:
   - Start backend: `uvicorn app.main:app --reload`
   - Start frontend: `cd frontend && npm run dev`
   - Register a user, upload a PDF, ask a question, verify citations

2. **Docker deployment**:
   - `docker-compose up --build`
   - Verify all containers healthy

3. **Optional hardening**:
   - Persist conversation history to DB (currently in-memory, expires on restart)
   - Add PostgreSQL for production (swap `DATABASE_URL` to `postgresql+asyncpg://...`)
   - Add Alembic migration for any new tables
