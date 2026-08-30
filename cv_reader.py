"""
CV text extraction for Application Fit Analyzer.

Reads CVs entirely in memory - nothing is written to disk at any point.
Accepts .pdf and .docx via MarkItDown, or plain pasted text.
"""

import io
from markitdown import MarkItDown

MAX_FILE_BYTES = 5 * 1024 * 1024
MAX_CHARS = 40000
MIN_CHARS = 100


class CVReadError(Exception):
    """Raised when a CV cannot be read. Message is safe to show a user."""


def extract_from_upload(file_bytes, filename=""):
    """Extract text from PDF or DOCX bytes. Nothing touches disk."""
    if not file_bytes:
        raise CVReadError("The uploaded file is empty.")

    if len(file_bytes) > MAX_FILE_BYTES:
        mb = len(file_bytes) / (1024 * 1024)
        raise CVReadError(
            f"File is {mb:.1f}MB. Please upload a CV under "
            f"{MAX_FILE_BYTES // (1024 * 1024)}MB."
        )

    try:
        result = MarkItDown().convert(io.BytesIO(file_bytes))
        text = result.text_content
    except Exception as exc:
        raise CVReadError(
            "Could not read that file. Please upload a PDF or Word document, "
            "or paste your CV as text instead."
        ) from exc

    return _validate(text)


def extract_from_text(raw_text):
    """Accept a pasted CV."""
    if not raw_text or not raw_text.strip():
        raise CVReadError("No CV text provided.")
    return _validate(raw_text)


def _validate(text):
    text = (text or "").strip()

    if len(text) < MIN_CHARS:
        raise CVReadError(
            "Could not find enough readable text. If your CV is a scanned "
            "image, please paste the text instead."
        )

    if len(text) > MAX_CHARS:
        text = text[:MAX_CHARS]

    return text
