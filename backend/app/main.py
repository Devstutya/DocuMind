from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.auth.routes import router as auth_router
from app.demo.routes import router as demo_router
from app.documents.routes import router as documents_router
from app.rag.routes import router as rag_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: create DB tables on startup (dev convenience).

    In production, run ``alembic upgrade head`` before starting the server
    so that schema migrations are applied in a controlled, auditable way.
    """
    # Import here to avoid circular imports at module load time.
    from app.database import Base, engine
    import app.db_models  # noqa: F401 — registers ORM models with Base

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield
    # Nothing to clean up at shutdown for SQLite.


app = FastAPI(
    title="DocuMind API",
    description="RAG-powered document Q&A system",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "DocuMind API", "version": "1.0.0"}


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(demo_router, prefix="/api/demo", tags=["demo"])
app.include_router(documents_router, prefix="/api/documents", tags=["documents"])
app.include_router(rag_router, prefix="/api/rag", tags=["rag"])
