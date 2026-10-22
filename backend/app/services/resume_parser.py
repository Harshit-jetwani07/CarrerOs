"""
Extracts raw text from an uploaded resume file (PDF or DOCX).
This is deliberately separate from AI analysis: text extraction is a
plain deterministic step, structuring/scoring is the AI's job.
"""
import io

import fitz  # PyMuPDF
import docx


def extract_text(filename: str, file_bytes: bytes) -> str:
    lower = filename.lower()
    if lower.endswith(".pdf"):
        return _extract_pdf(file_bytes)
    if lower.endswith(".docx"):
        return _extract_docx(file_bytes)
    raise ValueError("Unsupported file type. Please upload a PDF or DOCX resume.")


def _extract_pdf(file_bytes: bytes) -> str:
    text_parts = []
    with fitz.open(stream=file_bytes, filetype="pdf") as pdf:
        for page in pdf:
            text_parts.append(page.get_text())
    return "\n".join(text_parts).strip()


def _extract_docx(file_bytes: bytes) -> str:
    document = docx.Document(io.BytesIO(file_bytes))
    return "\n".join(p.text for p in document.paragraphs).strip()
