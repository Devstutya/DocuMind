# DocuMind - AI-Powered Document Q&A System

DocuMind is a Retrieval-Augmented Generation (RAG) system that allows users to upload PDF documents and ask questions, receiving contextual answers with source citations. Supports both a no-auth demo mode and full authenticated access with document management and conversation history.

## Features

- **PDF Upload & Processing**: Upload PDF documents with automatic text extraction and chunking
- **AI-Powered Q&A**: Ask questions about your documents using GPT-4o-mini
- **Source Citations**: Get answers with references to specific pages and text snippets
- **Conversation Memory**: Context-aware follow-up questions with a 5-turn sliding window
- **Demo Mode**: Try the system instantly without creating an account
- **User Authentication**: Secure JWT-based authentication with bcrypt password hashing
- **Document Management**: View, manage, and delete uploaded documents from the dashboard
- **Rate Limiting**: Sliding-window rate limiting (20 req/min per user) for API stability
- **Structured Logging**: JSON-formatted logs with query timing and source counts
- **Docker Support**: Multi-container deployment with Docker Compose

## Tech Stack

### Backend
- FastAPI (Python 3.11+) — async API server
- LangChain — RAG orchestration
- OpenAI GPT-4o-mini — answer generation
- OpenAI text-embedding-3-small — 1536-dim vector embeddings
- Pinecone (serverless) — vector similarity search
- SQLite (dev) / PostgreSQL (prod) — user and document persistence
- SQLAlchemy 2.0 async + Alembic — ORM and migrations
- PyMuPDF — PDF text extraction
- JWT + passlib/bcrypt — authentication

### Frontend
- React 18 + Vite
- Tailwind CSS
- React Router
- Lucide React icons

## Prerequisites

- Python 3.11 or higher
- Node.js 18 or higher
- Docker and Docker Compose (for containerized deployment)
- OpenAI API key ([platform.openai.com/api-keys](https://platform.openai.com/api-keys))
- Pinecone API key and index named `documind` (1536 dimensions, cosine metric)

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd documind
```

### 2. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and fill in your credentials:

```env
OPENAI_API_KEY=sk-your-openai-api-key
PINECONE_API_KEY=your-pinecone-api-key
PINECONE_INDEX_NAME=documind
JWT_SECRET_KEY=your-secret-key  # Generate with: openssl rand -hex 32
```

### 3. Option A: Docker Deployment

```bash
# Build and start all services
docker-compose up --build

# Backend available at http://localhost:8000
# Frontend available at http://localhost:5173
```

### 4. Option B: Local Development

#### Backend

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn app.main:app --reload
# Backend available at http://localhost:8000
```

#### Frontend

```bash
cd frontend
npm install
npm run dev
# Frontend available at http://localhost:5173
```

## API Documentation

Once the backend is running:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Key Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/auth/register` | No | Create a new account |
| POST | `/api/auth/login` | No | Obtain JWT token |
| GET | `/api/auth/me` | Yes | Get current user info |
| POST | `/api/documents/upload` | Yes | Upload and index a PDF |
| GET | `/api/documents/` | Yes | List user's documents |
| DELETE | `/api/documents/{id}` | Yes | Delete document and its vectors |
| POST | `/api/rag/query` | Yes | Ask a question (rate-limited) |
| GET | `/api/rag/conversations/{id}` | No | Retrieve conversation history |
| POST | `/api/demo/upload` | No | Demo mode — upload without auth |
| GET | `/api/health` | No | Health check |

## Project Structure

```
documind/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point, lifespan setup
│   │   ├── config.py            # Pydantic Settings, env vars
│   │   ├── models.py            # Pydantic request/response schemas
│   │   ├── database.py          # Async SQLAlchemy engine, get_db
│   │   ├── db_models.py         # UserModel, DocumentModel ORM models
│   │   ├── auth/                # JWT creation/validation, login/register routes
│   │   ├── demo/                # Unauthenticated demo upload endpoint
│   │   ├── documents/           # PDF parsing, chunking, embeddings, upload routes
│   │   ├── rag/                 # Pinecone retriever, LangChain chain, memory, query routes
│   │   └── utils/               # Structured JSON logging, rate limiting
│   ├── alembic/                 # Database migrations
│   ├── tests/
│   │   ├── test_routes/         # Endpoint integration tests
│   │   ├── test_rag/            # RAG pipeline tests
│   │   └── test_utils/          # Rate limiter tests
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatInterface.jsx      # Main Q&A interface
│   │   │   ├── DocumentUpload.jsx     # PDF upload with drag-and-drop
│   │   │   ├── SourceCitation.jsx     # Per-answer citation display
│   │   │   └── Sidebar.jsx            # Dashboard navigation
│   │   ├── pages/
│   │   │   ├── Home.jsx               # Landing page (demo vs full access)
│   │   │   ├── Login.jsx              # Auth page (login/register)
│   │   │   └── Dashboard.jsx          # Full dashboard (chat, docs, history, settings)
│   │   ├── services/
│   │   │   └── api.js                 # Axios API client
│   │   ├── App.jsx                    # React Router setup
│   │   └── main.jsx
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

## Configuration Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `CHUNK_SIZE` | `1000` | Text chunk size in characters |
| `CHUNK_OVERLAP` | `200` | Overlap between adjacent chunks |
| `TOP_K_RESULTS` | `5` | Chunks retrieved per query |
| `MEMORY_WINDOW_SIZE` | `5` | Conversation turns kept in memory |
| `RATE_LIMIT_PER_MINUTE` | `20` | Max API requests per user per minute |
| `MAX_FILE_SIZE_MB` | `50` | Maximum PDF upload size |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | JWT token lifetime |

## Usage

1. **Demo mode**: Click "Try a Demo" on the landing page — upload a PDF and ask questions immediately, no account required.
2. **Full access**: Click "Get Started" to register, then use the dashboard for persistent document management and chat history.
3. **Upload documents**: Drag-and-drop or click to upload PDFs from the Upload tab.
4. **Ask questions**: Type questions in the Chat interface; answers include page-level citations.
5. **Follow-up questions**: The system remembers the last 5 turns for contextual follow-ups.

## Running Tests

```bash
cd backend
pytest tests/ -v
# 62/62 tests passing
```

## Performance Targets

| Metric | Target |
|--------|--------|
| Answer relevance | 90%+ |
| Query latency | <1 second |
| Vector search | <200ms |
| Document capacity | 500+ PDFs (100K Pinecone vectors) |
| Follow-up reduction | 35% fewer follow-ups via conversation memory |

## Production Notes

- Swap `DATABASE_URL` to `postgresql+asyncpg://...` to use PostgreSQL instead of SQLite
- Conversation memory is in-process — restart clears it; persist to DB for durability
- Pinecone free tier: 1 index, 100K vectors (sufficient for ~500 documents)
- All structured logs are JSON; pipe to any log aggregator

## License

MIT License — see [LICENSE](LICENSE) for details.
