# DocuMind — RAG Knowledge Assistant
## Project Plan & Implementation Guide

---

## Overview

DocuMind is an AI-powered document Q&A system that lets users upload PDFs and ask questions with contextual citations. It uses a Retrieval-Augmented Generation (RAG) pipeline with LangChain, OpenAI embeddings, Pinecone vector database, and a FastAPI + React stack.

**Target Features (from your resume):**
- Semantic search across 500+ PDFs with citations
- Sub-second query latency via hybrid search
- Conversation memory with sliding window context
- Production deployment with Docker, auth, rate limiting, logging

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React+Vite, Tailwind CSS |
| Backend | FastAPI (Python) |
| LLM Framework | LangChain |
| LLM | OpenAI GPT-4 / GPT-4o-mini |
| Embeddings | OpenAI text-embedding-3-small |
| Vector DB | Pinecone (free tier works) |
| PDF Processing | PyMuPDF (fitz), pdfplumber |
| Auth | JWT tokens |
| Containerization | Docker, Docker Compose |

---

## Current Status

**COMPLETED:**
- Frontend structure with React + Vite + Tailwind CSS
- Landing page with dual-path navigation (demo vs. full access)
- Demo mode implementation (try before authentication)
- Full dashboard with sidebar navigation
- Base components: ChatInterface, DocumentUpload, SourceCitation, Sidebar
- Routing setup between all pages

**IN PROGRESS:**
- Backend API implementation (Phases 1-4: PDF processing, chunking, embeddings, Pinecone, RAG chain)

**TODO:**
- Backend RAG pipeline (Phases 1-4)
- Docker setup for backend (Phase 5 - early validation)
- Conversation memory (Phase 6)
- Frontend-backend integration (Phase 7)
- Authentication system (Phase 8)
- Styling/improving UI/UX (polish, animations, accessibility)
- Full deployment (Phase 8)

---

## Project Structure

```
documind/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app entry
│   │   ├── config.py            # Settings & env vars
│   │   ├── models.py            # Pydantic schemas
│   │   ├── auth/
│   │   │   ├── __init__.py
│   │   │   ├── jwt.py           # Token creation/validation
│   │   │   └── routes.py        # Login/register endpoints
│   │   ├── documents/
│   │   │   ├── __init__.py
│   │   │   ├── parser.py        # PDF text extraction
│   │   │   ├── chunker.py       # Recursive text chunking
│   │   │   ├── embeddings.py    # OpenAI embedding calls
│   │   │   └── routes.py        # Upload/delete endpoints
│   │   ├── rag/
│   │   │   ├── __init__.py
│   │   │   ├── retriever.py     # Pinecone query logic
│   │   │   ├── chain.py         # LangChain QA chain
│   │   │   ├── memory.py        # Conversation memory
│   │   │   └── routes.py        # Query endpoint
│   │   └── utils/
│   │       ├── logging.py       # Structured logging
│   │       └── rate_limit.py    # Rate limiting middleware
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/                     [STRUCTURE COMPLETE]
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatInterface.jsx      [Created]
│   │   │   ├── DocumentUpload.jsx     [Created]
│   │   │   ├── SourceCitation.jsx     [Created]
│   │   │   └── Sidebar.jsx            [Created]
│   │   ├── pages/
│   │   │   ├── Home.jsx               [Landing page with dual CTAs]
│   │   │   ├── Login.jsx              [Auth page]
│   │   │   ├── DemoPage.jsx           [Demo mode (no auth)]
│   │   │   └── Dashboard.jsx          [Full dashboard with sidebar]
│   │   ├── hooks/
│   │   │   └── useChat.js
│   │   ├── services/
│   │   │   └── api.js                 [Created]
│   │   ├── App.jsx                    [Routing configured]
│   │   └── main.jsx                   [Entry point]
│   ├── package.json
│   ├── Dockerfile
│   └── tailwind.config.js
├── docker-compose.yml
└── README.md
```

---

## User Flow Architecture

### Demo Mode vs. Full Access

**Path 1: Demo Mode (No Authentication)**
```
Landing Page → "Try a Demo" → DemoPage
- Allows immediate PDF upload and chat
- No account required
- Data not persisted
- "Get Started" button visible to convert to full access
```

**Path 2: Full Access (Authentication Required)**
```
Landing Page → "Get Started" → Login/Register → Dashboard
- Full sidebar navigation
- Document management
- Chat history
- Settings & profile
- Persistent data
```

**Dashboard Features (Sidebar Navigation):**
- Chat: Main Q&A interface
- My Documents: View/manage uploaded PDFs
- Chat History: Browse previous conversations
- Upload: Dedicated document upload
- Settings: AI model, retrieval config
- Profile: User info, usage stats

---

## Implementation Phases

### Phase 1: Project Setup & PDF Processing (Days 1-2) [IN PROGRESS]

**Goals:** Set up project structure, implement PDF upload and text extraction.

**Tasks:**
1. [DONE] Initialize project directories
2. [DONE] Set up frontend structure (React + Vite)
3. [TODO] Set up Python virtual environment
4. [TODO] Create FastAPI skeleton with health check endpoint
5. [TODO] Implement PDF text extraction with PyMuPDF
6. [TODO] Test with sample PDFs

**Key Code — PDF Parser (`backend/app/documents/parser.py`):**
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

**Deliverables:**
- [x] Frontend project structure complete (React + Vite + Tailwind)
- [x] All frontend pages and components created
- [ ] FastAPI app running locally
- [ ] PDF upload endpoint accepting files
- [ ] Text extraction working on test PDFs

---

### Phase 2: Text Chunking & Embeddings (Days 3-4)

**Goals:** Implement recursive text chunking, generate embeddings with OpenAI.

**Tasks:**
1. Implement recursive character text splitter
2. Add metadata to chunks (doc_id, page, chunk_index)
3. Set up OpenAI API client
4. Generate embeddings for chunks
5. Test embedding quality with sample queries

**Key Code — Recursive Chunker (`backend/app/documents/chunker.py`):**
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

**Key Code — Embeddings (`backend/app/documents/embeddings.py`):**
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

**Chunking Strategy Tips:**
- Start with 1000 chars, 200 overlap — adjust based on your docs
- Preserve sentence boundaries when possible
- Store page numbers for citation accuracy

**Deliverables:**
- [ ] Chunking produces consistent, overlapping segments
- [ ] Embeddings generated successfully
- [ ] Metadata attached to each chunk

---

### Phase 3: Pinecone Vector Storage (Days 5-6)

**Goals:** Set up Pinecone, implement upsert and query operations.

**Tasks:**
1. Create Pinecone account (free tier: 1 index, 100K vectors)
2. Initialize index with correct dimensions (1536 for text-embedding-3-small)
3. Implement batch upsert for document chunks
4. Implement similarity search with metadata filtering
5. Add document deletion by doc_id

**Key Code — Pinecone Setup (`backend/app/rag/retriever.py`):**
```python
from pinecone import Pinecone, ServerlessSpec

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

# Create index (run once)
def create_index(index_name: str = "documind"):
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
                "text": chunk["text"][:1000]  # Store text in metadata for retrieval
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

**Deliverables:**
- [ ] Pinecone index created and accessible
- [ ] Documents upserted with metadata
- [ ] Similarity search returns relevant chunks
- [ ] Document deletion works

---

### Phase 4: RAG Chain & Query Endpoint (Days 7-9)

**Goals:** Build the LangChain QA chain, implement the query API.

**Tasks:**
1. Create retrieval chain with LangChain
2. Implement prompt template with context injection
3. Add source citation to responses
4. Build query endpoint with streaming support
5. Test end-to-end retrieval and generation

**Key Code — RAG Chain (`backend/app/rag/chain.py`):**
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
{context}
"""

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

def create_rag_chain(retriever_func):
    """Create RAG chain with retriever."""
    
    def retrieve_and_format(question: str) -> dict:
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

**Key Code — Query Endpoint (`backend/app/rag/routes.py`):**
```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/query", tags=["query"])

class QueryRequest(BaseModel):
    question: str
    conversation_id: str | None = None

class QueryResponse(BaseModel):
    answer: str
    sources: list[dict]

@router.post("/", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    try:
        # Get query embedding
        query_embedding = get_embeddings([request.question])[0]
        
        # Retrieve relevant chunks
        chunks = query_similar(query_embedding, top_k=5)
        
        if not chunks:
            return QueryResponse(
                answer="No relevant documents found.",
                sources=[]
            )
        
        # Generate answer
        context = format_context(chunks)
        answer = await generate_answer(request.question, context)
        
        return QueryResponse(
            answer=answer,
            sources=[{
                "page": c["page"],
                "doc_id": c["doc_id"],
                "snippet": c["text"][:200] + "..."
            } for c in chunks]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

**Deliverables:**
- [ ] RAG chain generates contextual answers
- [ ] Sources returned with page numbers
- [ ] Query endpoint responds in <2 seconds

---

### Phase 5: Docker Setup — Backend Only (Days 10-11)

**Goals:** Containerize the backend API for production-ready deployment and easier sharing.

**Tasks:**
1. Create backend Dockerfile
2. Set up docker-compose for backend
3. Lock down requirements.txt with exact versions
4. Add structured logging
5. Test complete RAG pipeline in Docker (PDF upload → query)
6. Write deployment documentation

**Key Code — Backend Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app/ ./app/

# Create non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Key Code — Docker Compose (Backend Only) (`docker-compose.yml`):**
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - PINECONE_API_KEY=${PINECONE_API_KEY}
      - UPLOAD_DIR=/app/uploads
    volumes:
      - ./uploads:/app/uploads
    restart: unless-stopped
```

**Key Code — Structured Logging (`backend/app/utils/logging.py`):**
```python
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
        }
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_obj)

def setup_logging():
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())

    logger = logging.getLogger("documind")
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    return logger

logger = setup_logging()
```

**Why Docker Now:**
- Validates complete RAG pipeline (PDF → embeddings → Pinecone → query) in production-like environment
- Locks down Python dependencies early, catching version conflicts before building more features
- Enables easy sharing: others can test with `docker-compose up` without local Python setup
- Allows parallel frontend integration work against consistent Dockerized backend

**Deliverables:**
- [ ] Backend Docker image builds successfully
- [ ] docker-compose starts backend and accepts requests
- [ ] Complete RAG flow works in Docker (upload PDF, query, get answer with sources)
- [ ] Logs output in JSON format
- [ ] requirements.txt pinned to specific versions

---

### Phase 6: Conversation Memory (Days 12-13)

**Goals:** Add multi-turn conversation support with sliding window context.

**Tasks:**
1. Implement conversation store (in-memory or Redis)
2. Add sliding window memory (keep last N turns)
3. Modify prompt to include conversation history
4. Handle follow-up questions with context
5. Update Docker container with memory support

**Key Code — Conversation Memory (`backend/app/rag/memory.py`):**
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

**Updated Prompt with History:**
```python
SYSTEM_PROMPT_WITH_MEMORY = """You are a helpful assistant that answers questions based on the provided context.

Previous conversation:
{history}

Context from documents:
{context}

Instructions:
- Answer based on the context and conversation history
- Reference previous answers when relevant
- Cite sources using [Page X] format
"""
```

**Deliverables:**
- [ ] Conversations persist across queries
- [ ] Follow-up questions work ("What about X?" after asking about Y)
- [ ] History auto-expires after inactivity
- [ ] Memory works in Dockerized backend

---

### Phase 7: Frontend Integration (Days 14-16) [MOSTLY COMPLETE]

**Goals:** Connect the existing React frontend to the Dockerized backend API.

**Completed:**
1. [DONE] React project with Vite + Tailwind
2. [DONE] Chat interface component
3. [DONE] Document upload component
4. [DONE] Source citations component
5. [DONE] Sidebar navigation
6. [DONE] Landing page with demo/full access paths
7. [DONE] Demo page (no auth required)
8. [DONE] Full dashboard with sidebar

**Remaining Tasks:**
1. Connect frontend API calls to Dockerized backend
2. Add drag-and-drop to document upload
3. Implement loading states and error handling
4. Add real-time chat functionality
5. Polish UI/UX (animations, transitions, accessibility)
6. Improve mobile responsiveness
7. Add toast notifications for user feedback
8. Test demo mode against Docker backend
9. Containerize frontend (optional for now)

**Key Code — Chat Interface (`frontend/src/components/ChatInterface.jsx`):**
```jsx
import { useState, useRef, useEffect } from 'react';
import { Send, Loader2 } from 'lucide-react';
import SourceCitation from './SourceCitation';

export default function ChatInterface({ conversationId }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(scrollToBottom, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await fetch('/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: input,
          conversation_id: conversationId
        })
      });

      const data = await response.json();
      
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: data.answer,
        sources: data.sources
      }]);
    } catch (error) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, something went wrong. Please try again.',
        error: true
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] rounded-lg p-3 ${
                msg.role === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-900'
              }`}
            >
              <p className="whitespace-pre-wrap">{msg.content}</p>
              {msg.sources && msg.sources.length > 0 && (
                <SourceCitation sources={msg.sources} />
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 rounded-lg p-3">
              <Loader2 className="w-5 h-5 animate-spin text-gray-500" />
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <form onSubmit={handleSubmit} className="p-4 border-t">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question about your documents..."
            className="flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </form>
    </div>
  );
}
```

**Key Code — Source Citation (`frontend/src/components/SourceCitation.jsx`):**
```jsx
import { FileText, ChevronDown, ChevronUp } from 'lucide-react';
import { useState } from 'react';

export default function SourceCitation({ sources }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="mt-3 pt-3 border-t border-gray-200">
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900"
      >
        <FileText className="w-4 h-4" />
        <span>{sources.length} source{sources.length !== 1 ? 's' : ''}</span>
        {expanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
      </button>
      
      {expanded && (
        <div className="mt-2 space-y-2">
          {sources.map((source, idx) => (
            <div
              key={idx}
              className="text-sm p-2 bg-white rounded border border-gray-200"
            >
              <div className="font-medium text-gray-700">
                Page {source.page}
              </div>
              <p className="text-gray-600 mt-1">{source.snippet}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
```

**Deliverables:**
- [x] Chat interface with message history
- [x] Document upload component
- [x] Expandable source citations
- [x] Responsive design (basic)
- [x] Landing page with dual navigation paths
- [x] Demo mode for unauthenticated users
- [x] Full dashboard with sidebar navigation
- [ ] Backend API integration with Docker
- [ ] Real-time chat updates
- [ ] Drag-and-drop file upload
- [ ] Loading states and error handling
- [ ] UI/UX polish (animations, transitions)
- [ ] Toast notifications

---

### Phase 8: Authentication & Full Deployment (Days 17-20)

**Goals:** Add JWT authentication, rate limiting, and finalize production deployment.

**Tasks:**
1. Implement user registration and login
2. Add JWT token generation and validation
3. Protect API routes with auth middleware
4. Add rate limiting per user
5. Sanitize inputs
6. Containerize frontend
7. Update docker-compose for full stack (backend + frontend)
8. Final deployment documentation
9. Production environment configuration

**Key Code — JWT Auth (`backend/app/auth/jwt.py`):**
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

**Key Code — Rate Limiting (`backend/app/utils/rate_limit.py`):**
```python
from fastapi import HTTPException, Request
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

**Key Code — Frontend Dockerfile:**
```dockerfile
FROM node:20-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

**Key Code — Full Stack Docker Compose (`docker-compose.yml`):**
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - PINECONE_API_KEY=${PINECONE_API_KEY}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
    volumes:
      - ./uploads:/app/uploads
    restart: unless-stopped

  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - backend
    restart: unless-stopped
```

**Deliverables:**
- [ ] User registration and login working
- [ ] Protected routes require valid JWT
- [ ] Rate limiting prevents abuse
- [ ] Passwords hashed with bcrypt
- [ ] Frontend containerized
- [ ] Full stack runs with docker-compose
- [ ] Production deployment documentation complete


## Environment Variables

Create a `.env` file:

```bash
# OpenAI
OPENAI_API_KEY=sk-...

# Pinecone
PINECONE_API_KEY=...

# Auth
JWT_SECRET_KEY=your-secret-key-here  # Generate with: openssl rand -hex 32

# App Config
UPLOAD_DIR=./uploads
MAX_FILE_SIZE_MB=50
```

---

## Testing & Evaluation

### Manual Testing Checklist
- [ ] Upload 5+ different PDFs (varying lengths, formats)
- [ ] Query with questions that span multiple documents
- [ ] Test follow-up questions ("What else?", "Can you elaborate?")
- [ ] Verify citations point to correct pages
- [ ] Test rate limiting by rapid requests
- [ ] Test with large files (>10MB PDFs)

### Metrics to Track (for resume claims)
1. **Answer Relevance**: Use RAGAS library or manual scoring (target: 92%+)
2. **Query Latency**: Measure time from query to first response token (target: <1 second)
3. **Document Count**: Track how many PDFs indexed (target: 500+)

**Simple Relevance Evaluation:**
```python
# Manual evaluation script
def evaluate_relevance(questions: list, expected_answers: list):
    scores = []
    for q, expected in zip(questions, expected_answers):
        response = query_endpoint(q)
        # Score 0-1 based on how well answer matches expected
        score = manual_score(response.answer, expected)
        scores.append(score)
    return sum(scores) / len(scores)
```

---

## Timeline Summary

| Phase | Days | Focus | Status |
|-------|------|-------|--------|
| 1 | 1-2 | Project setup, PDF extraction | IN PROGRESS (Frontend: DONE, Backend: TODO) |
| 2 | 3-4 | Chunking, embeddings | TODO |
| 3 | 5-6 | Pinecone integration | TODO |
| 4 | 7-9 | RAG chain, query API | TODO |
| 5 | 10-11 | Docker setup (backend only) | TODO |
| 6 | 12-13 | Conversation memory | TODO |
| 7 | 14-16 | Frontend integration | MOSTLY COMPLETE |
| 8 | 17-20 | Auth & full deployment | TODO |

**Total: ~20 days** (can compress to 2 weeks with focused effort)

**Current Progress:** Frontend structure complete (60% of Phase 7 done early). Backend Phases 1-6 remain. Docker moved to Phase 5 for early validation.

---

## Next Immediate Steps

**Frontend [READY]** - UI scaffolding complete, awaiting backend integration

**Backend - Focus Here:**
1. **This Week (Days 1-9):**
   - Phase 1: Set up FastAPI backend with PDF upload endpoint
   - Phase 2: Implement text chunking and OpenAI embeddings
   - Phase 3: Integrate Pinecone vector storage
   - Phase 4: Build RAG chain and query API

2. **Next Week (Days 10-16):**
   - Phase 5: Dockerize backend (CRITICAL MILESTONE - validates entire RAG pipeline)
   - Phase 6: Add conversation memory to Dockerized backend
   - Phase 7: Connect frontend to Dockerized backend API
   - Polish frontend UI/UX (parallel track)

3. **Week 3 (Days 17-20):**
   - Phase 8: Add JWT authentication, rate limiting
   - Containerize frontend
   - Finalize full-stack docker-compose
   - Production deployment documentation

**Priority Tasks (Backend Focus):**
- [ ] Create backend directory structure
- [ ] Set up Python virtual environment
- [ ] Install backend dependencies (FastAPI, LangChain, OpenAI, Pinecone, PyMuPDF)
- [ ] Create FastAPI main.py with health check
- [ ] Implement PDF upload endpoint
- [ ] Test PDF text extraction

**Parallel Track (Frontend Polish):**
- [ ] Add loading skeletons and transitions
- [ ] Implement drag-and-drop for file upload
- [ ] Add toast notifications for user actions
- [ ] Improve mobile responsiveness
- [ ] Add keyboard shortcuts and accessibility features
- [ ] Polish color scheme and typography
- [ ] Add smooth page transitions

**Key Changes:**
- Docker moved to Phase 5 (after RAG pipeline complete) for early validation
- Enables testing complete PDF → query flow in production-like environment
- Locks down dependencies early, catches conflicts before building more
- Frontend is ahead of schedule - ready to connect to Dockerized backend

**Note:** Frontend structure complete. Priority is building backend Phases 1-4, then immediately containerizing (Phase 5) to validate the RAG pipeline works end-to-end before adding more features.
