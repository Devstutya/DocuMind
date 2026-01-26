# DocuMind — RAG Knowledge Assistant

## Project Overview

DocuMind is an AI-powered document Q&A system using Retrieval-Augmented Generation (RAG). Users upload PDFs and ask questions, receiving answers with contextual citations.

## Tech Stack

- **Backend**: FastAPI (Python 3.11+)
- **Frontend**: React + Vite + Tailwind CSS
- **LLM Framework**: LangChain
- **LLM**: OpenAI GPT-4o-mini
- **Embeddings**: OpenAI text-embedding-3-small (1536 dimensions)
- **Vector DB**: Pinecone (serverless, free tier)
- **PDF Processing**: PyMuPDF (fitz)
- **Auth**: JWT with python-jose + passlib
- **Containerization**: Docker + Docker Compose

## Project Structure

```
documind/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── config.py            # Settings & env vars
│   │   ├── models.py            # Pydantic schemas
│   │   ├── auth/                # JWT auth
│   │   ├── documents/           # PDF parsing, chunking, embeddings
│   │   ├── rag/                 # Retriever, chain, memory
│   │   └── utils/               # Logging, rate limiting
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/          # ChatInterface, DocumentUpload, SourceCitation
│   │   ├── pages/               # Home, Login, Dashboard
│   │   ├── hooks/
│   │   └── services/api.js
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── .env
└── README.md
```

## Key Features to Implement

1. **PDF Upload & Processing**: Extract text with PyMuPDF, chunk with RecursiveCharacterTextSplitter (1000 chars, 200 overlap)
2. **Vector Storage**: Embed chunks with OpenAI, store in Pinecone with metadata (doc_id, page, chunk_index)
3. **RAG Query Pipeline**: Retrieve top-5 similar chunks, inject into prompt, generate answer with citations
4. **Conversation Memory**: Sliding window (last 5 turns) for follow-up questions
5. **Source Citations**: Return page numbers and snippets with each answer
6. **Auth**: JWT tokens, bcrypt password hashing
7. **Rate Limiting**: 20 requests/minute per user
8. **Docker Deployment**: Multi-container setup with Docker Compose

## Current Phase

Phase 1: Project setup and PDF text extraction

## Commands

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev

# Docker
docker-compose up --build
```

## Environment Variables (.env)

```
OPENAI_API_KEY=sk-...
PINECONE_API_KEY=...
JWT_SECRET_KEY=...  # Generate with: openssl rand -hex 32
UPLOAD_DIR=./uploads
MAX_FILE_SIZE_MB=50
```

## Dependencies

### Backend (requirements.txt)
```
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
python-multipart>=0.0.6
langchain>=0.1.0
langchain-openai>=0.0.5
openai>=1.10.0
pinecone-client>=3.0.0
pymupdf>=1.23.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
pydantic>=2.5.0
pydantic-settings>=2.1.0
```

### Frontend (package.json dependencies)
```
react, react-dom, react-router-dom, lucide-react, tailwindcss
```

## Code Style

- Python: Use type hints, async/await for I/O operations
- Keep functions small and focused
- Add docstrings to public functions
- Use Pydantic models for request/response validation
- Frontend: Functional components with hooks

## Resume Claims to Validate

When building, track these metrics:
- Answer relevance: Target 92%+ on evaluation benchmarks
- Query latency: Target sub-second (<1s)
- Document capacity: Support 500+ PDFs
- Follow-up reduction: 35% fewer follow-up queries with conversation memory

## Notes

- Pinecone free tier: 1 index, 100K vectors — enough for 500+ docs
- Use GPT-4o-mini for cost efficiency during development
- Chunk text stored in Pinecone metadata (truncated to 1000 chars)
- All API routes under `/api/` prefix
