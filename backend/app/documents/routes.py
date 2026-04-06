# backend/app/documents/routes.py
import os
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, UploadFile

from app.auth.jwt import get_current_user
from app.config import settings
from app.documents.chunker import chunk_document
from app.documents.parser import extract_text_from_pdf
from app.models import DocumentList, DocumentMetadata, DocumentUploadResponse

router = APIRouter()

# In-memory document store:
#   { doc_id: {"document_id": str, "filename": str, "page_count": int,
#              "chunk_count": int, "uploaded_at": datetime, "user_id": str,
#              "file_path": str} }
# Replaced with a real database in a future phase.
_documents: dict[str, dict] = {}


def _ensure_upload_dir() -> str:
    """Return the resolved upload directory path, creating it if absent."""
    upload_dir = os.path.abspath(settings.UPLOAD_DIR)
    os.makedirs(upload_dir, exist_ok=True)
    return upload_dir


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=201,
    summary="Upload a PDF document",
    responses={
        201: {"description": "Document uploaded and processed successfully"},
        400: {"description": "File is not a PDF or exceeds the size limit"},
        401: {"description": "Missing or invalid token"},
    },
)
async def upload_document(
    file: UploadFile,
    current_user_id: str = Depends(get_current_user),
) -> DocumentUploadResponse:
    """Upload and process a PDF document for the authenticated user.

    Validates that the file is a PDF and within the configured size limit,
    then extracts text and splits it into overlapping chunks. Embedding and
    vector storage are deferred to Phase 3 — this endpoint returns immediately
    with ``status="processed"`` once chunking is complete.

    The file is persisted to ``UPLOAD_DIR`` under a UUID-based filename to
    avoid collisions.

    Example request::

        POST /api/documents/upload
        Authorization: Bearer <jwt>
        Content-Type: multipart/form-data
        (binary PDF payload)

    Example response::

        {
          "document_id": "d1e2f3...",
          "filename": "report.pdf",
          "page_count": 12,
          "chunk_count": 47,
          "status": "processed",
          "message": "Document uploaded and processed successfully"
        }
    """
    # --- Content-type validation ------------------------------------------
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are accepted. Received: " + (file.content_type or "unknown"),
        )

    # --- Read payload and enforce size limit --------------------------------
    max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    contents = await file.read()

    if len(contents) > max_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"File exceeds the maximum allowed size of {settings.MAX_FILE_SIZE_MB} MB.",
        )

    # --- Persist to disk ----------------------------------------------------
    doc_id = str(uuid.uuid4())
    upload_dir = _ensure_upload_dir()
    # Use <doc_id>.pdf so the stored name is always unique and unambiguous.
    file_path = os.path.join(upload_dir, f"{doc_id}.pdf")

    with open(file_path, "wb") as f:
        f.write(contents)

    # --- Extract and chunk --------------------------------------------------
    try:
        pages = extract_text_from_pdf(file_path)
    except Exception as exc:
        # Remove the orphaned file before surfacing the error.
        os.remove(file_path)
        raise HTTPException(
            status_code=400,
            detail=f"Failed to parse PDF: {exc}",
        ) from exc

    chunks = chunk_document(
        pages,
        doc_id=doc_id,
        chunk_size=settings.CHUNK_SIZE,
        overlap=settings.CHUNK_OVERLAP,
    )

    # --- Persist metadata to in-memory store --------------------------------
    original_filename = file.filename or f"{doc_id}.pdf"
    _documents[doc_id] = {
        "document_id": doc_id,
        "filename": original_filename,
        "page_count": len(pages),
        "chunk_count": len(chunks),
        "uploaded_at": datetime.utcnow(),
        "user_id": current_user_id,
        "file_path": file_path,
    }

    return DocumentUploadResponse(
        document_id=doc_id,
        filename=original_filename,
        page_count=len(pages),
        chunk_count=len(chunks),
        status="processed",
        message="Document uploaded and processed successfully",
    )


@router.get(
    "/",
    response_model=DocumentList,
    summary="List documents owned by the authenticated user",
    responses={
        200: {"description": "Paginated list of the user's documents"},
        401: {"description": "Missing or invalid token"},
    },
)
async def list_documents(
    current_user_id: str = Depends(get_current_user),
) -> DocumentList:
    """Return all documents uploaded by the currently authenticated user.

    Example request::

        GET /api/documents/
        Authorization: Bearer <jwt>

    Example response::

        {
          "documents": [
            {
              "document_id": "d1e2f3...",
              "filename": "report.pdf",
              "page_count": 12,
              "chunk_count": 47,
              "uploaded_at": "2026-04-06T12:00:00",
              "user_id": "u9a8b7..."
            }
          ],
          "total": 1
        }
    """
    user_docs = [
        DocumentMetadata(
            document_id=doc["document_id"],
            filename=doc["filename"],
            page_count=doc["page_count"],
            chunk_count=doc["chunk_count"],
            uploaded_at=doc["uploaded_at"],
            user_id=doc["user_id"],
        )
        for doc in _documents.values()
        if doc["user_id"] == current_user_id
    ]
    return DocumentList(documents=user_docs, total=len(user_docs))


@router.delete(
    "/{document_id}",
    status_code=204,
    summary="Delete a document owned by the authenticated user",
    responses={
        204: {"description": "Document deleted successfully"},
        401: {"description": "Missing or invalid token"},
        403: {"description": "Document belongs to a different user"},
        404: {"description": "Document not found"},
    },
)
async def delete_document(
    document_id: str,
    current_user_id: str = Depends(get_current_user),
) -> None:
    """Delete a document and its file from disk.

    Only the owning user may delete a document. Attempting to delete another
    user's document returns 403 rather than 404 to be explicit about
    authorization failure vs. a missing resource.

    Example request::

        DELETE /api/documents/d1e2f3...
        Authorization: Bearer <jwt>
    """
    doc = _documents.get(document_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")

    if doc["user_id"] != current_user_id:
        raise HTTPException(status_code=403, detail="Access denied: document belongs to another user")

    # Remove file from disk (best-effort; don't fail the request if already gone).
    file_path: str = doc.get("file_path", "")
    if file_path and os.path.exists(file_path):
        os.remove(file_path)

    del _documents[document_id]
