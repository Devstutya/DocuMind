from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings

app = FastAPI(
    title="DocuMind API",
    description="RAG-powered document Q&A system",
    version="1.0.0"
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

# TODO: Import and include routers for auth, documents, and RAG endpoints
# from app.auth.routes import router as auth_router
# from app.documents.routes import router as documents_router
# from app.rag.routes import router as rag_router
#
# app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
# app.include_router(documents_router, prefix="/api/documents", tags=["documents"])
# app.include_router(rag_router, prefix="/api/rag", tags=["rag"])
