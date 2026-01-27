# DocuMind - AI-Powered Document Q&A System

DocuMind is a Retrieval-Augmented Generation (RAG) system that allows users to upload PDF documents and ask questions, receiving contextual answers with source citations.

## Features

- **PDF Upload & Processing**: Upload PDF documents with automatic text extraction and chunking
- **AI-Powered Q&A**: Ask questions about your documents using GPT-4o-mini
- **Source Citations**: Get answers with references to specific pages and text snippets
- **Conversation Memory**: Context-aware follow-up questions with conversation history
- **User Authentication**: Secure JWT-based authentication
- **Rate Limiting**: Built-in API rate limiting for stability
- **Docker Support**: Easy deployment with Docker Compose

## Tech Stack

### Backend
- FastAPI (Python 3.11+)
- LangChain for RAG pipeline
- OpenAI GPT-4o-mini for answers
- OpenAI text-embedding-3-small for embeddings
- Pinecone for vector storage
- PyMuPDF for PDF processing
- JWT authentication with bcrypt

### Frontend
- React 18
- Vite
- Tailwind CSS
- React Router
- Lucide React icons

## Prerequisites

- Python 3.11 or higher
- Node.js 18 or higher
- Docker and Docker Compose (for containerized deployment)
- OpenAI API key
- Pinecone API key

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

Edit `.env` and add your API keys:

```env
OPENAI_API_KEY=sk-your-openai-api-key
PINECONE_API_KEY=your-pinecone-api-key
JWT_SECRET_KEY=your-secret-key  # Generate with: openssl rand -hex 32
```

### 3. Option A: Docker Deployment (Recommended)

```bash
# Build and start all services
docker-compose up --build

# Backend will be available at http://localhost:8000
# Frontend will be available at http://localhost:5173
```

### 4. Option B: Local Development

#### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the backend
uvicorn app.main:app --reload

# Backend will be available at http://localhost:8000
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run the development server
npm run dev

# Frontend will be available at http://localhost:5173
```

## API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
documind/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── config.py            # Settings & environment variables
│   │   ├── models.py            # Pydantic schemas
│   │   ├── auth/                # JWT authentication
│   │   ├── documents/           # PDF parsing, chunking, embeddings
│   │   ├── rag/                 # Retriever, chain, memory
│   │   └── utils/               # Logging, rate limiting
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/          # React components
│   │   │   ├── ChatInterface.jsx
│   │   │   ├── DocumentUpload.jsx
│   │   │   └── SourceCitation.jsx
│   │   ├── pages/               # Page components
│   │   │   ├── Home.jsx
│   │   │   ├── Login.jsx
│   │   │   └── Dashboard.jsx
│   │   ├── services/
│   │   │   └── api.js           # API client
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── .env
└── README.md
```

## Configuration

Key configuration options in `.env`:

- `CHUNK_SIZE`: Size of text chunks (default: 1000 characters)
- `CHUNK_OVERLAP`: Overlap between chunks (default: 200 characters)
- `TOP_K_RESULTS`: Number of similar chunks to retrieve (default: 5)
- `MEMORY_WINDOW_SIZE`: Number of conversation turns to remember (default: 5)
- `RATE_LIMIT_PER_MINUTE`: API rate limit per user (default: 20)
- `MAX_FILE_SIZE_MB`: Maximum PDF file size (default: 50MB)

## Usage

1. **Register/Login**: Create an account or login at http://localhost:5173/login
2. **Upload Documents**: Click the upload area to add PDF documents
3. **Ask Questions**: Type questions in the chat interface
4. **View Sources**: See relevant document excerpts with page numbers for each answer
5. **Follow-up Questions**: Continue the conversation with context-aware follow-ups

## Development Roadmap

- [x] Project structure setup
- [ ] Auth implementation (JWT, user management)
- [ ] PDF processing (text extraction, chunking)
- [ ] Vector database integration (Pinecone)
- [ ] RAG pipeline (retrieval, generation, citations)
- [ ] Conversation memory
- [ ] Rate limiting
- [ ] Frontend-backend integration
- [ ] Testing & optimization
- [ ] Deployment documentation

## Performance Targets

- Answer relevance: 90%+ on evaluation benchmarks
- Query latency: <1 second
- Document capacity: 500+ PDFs
- Follow-up query reduction: 35% with conversation memory

## Contributing

See [CLAUDE.md](CLAUDE.md) for detailed implementation guidelines and coding standards.

## License

MIT License - see [LICENSE](LICENSE) file for details
