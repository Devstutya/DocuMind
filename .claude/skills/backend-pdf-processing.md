# PDF Processing Pipeline

- PDFs are uploaded via `/api/v1/documents/upload`
- Stored temporarily in `/tmp/uploads/`, then moved to object storage
- Text extraction uses PyMuPDF (fitz)
- Chunking strategy: 512 tokens per chunk, 50 token overlap
- Embeddings generated via OpenAI `text-embedding-3-small`
- Chunks stored in `document_chunks` table with vector column