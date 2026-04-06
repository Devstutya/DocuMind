# backend/app/demo/routes.py
import os
import uuid

from fastapi import APIRouter, HTTPException, UploadFile

from app.config import settings
from app.documents.chunker import chunk_document
from app.documents.embeddings import get_embeddings
from app.documents.parser import extract_text_from_pdf
from app.models import DocumentUploadResponse
from app.rag.retriever import upsert_chunks

router = APIRouter()

DEMO_USER_ID = "demo"


def _ensure_upload_dir() -> str:
    upload_dir = os.path.abspath(settings.UPLOAD_DIR)
    os.makedirs(upload_dir, exist_ok=True)
    return upload_dir


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=201,
    summary="Upload a PDF in demo mode (no authentication required)",
)
async def demo_upload(file: UploadFile) -> DocumentUploadResponse:
    """Upload and process a single PDF without authentication.

    Intended for the public demo experience. Data is processed the same way
    as authenticated uploads but associated with the shared 'demo' user.
    """
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are accepted. Received: " + (file.content_type or "unknown"),
        )

    max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    contents = await file.read()

    if len(contents) > max_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"File exceeds the maximum allowed size of {settings.MAX_FILE_SIZE_MB} MB.",
        )

    doc_id = str(uuid.uuid4())
    upload_dir = _ensure_upload_dir()
    file_path = os.path.join(upload_dir, f"{doc_id}.pdf")

    with open(file_path, "wb") as f:
        f.write(contents)

    try:
        pages = extract_text_from_pdf(file_path)
    except Exception as exc:
        os.remove(file_path)
        raise HTTPException(status_code=400, detail=f"Failed to parse PDF: {exc}") from exc

    chunks = chunk_document(
        pages,
        doc_id=doc_id,
        chunk_size=settings.CHUNK_SIZE,
        overlap=settings.CHUNK_OVERLAP,
    )

    try:
        chunk_texts = [chunk["text"] for chunk in chunks]
        embeddings = get_embeddings(chunk_texts)
        upsert_chunks(chunks, embeddings)
    except Exception as exc:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Failed to embed and index document: {exc}") from exc

    return DocumentUploadResponse(
        document_id=doc_id,
        filename=file.filename or f"{doc_id}.pdf",
        page_count=len(pages),
        chunk_count=len(chunks),
        status="processed",
        message="Document uploaded and processed successfully",
    )
