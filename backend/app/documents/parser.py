# backend/app/documents/parser.py
import fitz  # PyMuPDF


def extract_text_from_pdf(file_path: str) -> list[dict]:
    """Extract text from a PDF file, one entry per non-empty page.

    Args:
        file_path: Absolute or relative path to the PDF file on disk.

    Returns:
        List of dicts with keys ``page`` (1-based int) and ``text`` (str).
        Pages that contain only whitespace are omitted.

    Example::

        pages = extract_text_from_pdf("/uploads/report.pdf")
        # [{"page": 1, "text": "Introduction..."}, {"page": 2, "text": "..."}, ...]
    """
    doc = fitz.open(file_path)
    pages: list[dict] = []
    for page_num, page in enumerate(doc, 1):
        text: str = page.get_text("text")
        if text.strip():
            pages.append({"page": page_num, "text": text.strip()})
    doc.close()
    return pages
