"""
PDF processing utilities for AI Study Companion.
Handles text extraction, chunking, and page-level parsing.
"""

import pdfplumber
import os


def extract_text(file_path: str) -> str:
    """
    Extract all text from a PDF file using pdfplumber.
    Returns the full text as a single string.
    """
    full_text = []
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    full_text.append(text)
    except Exception as e:
        raise RuntimeError(f"Failed to extract text from PDF: {e}")

    return "\n\n".join(full_text)


def extract_pages(file_path: str) -> list[tuple[int, str]]:
    """
    Extract text page by page from a PDF.
    Returns a list of (page_number, text) tuples (1-indexed).
    """
    pages = []
    try:
        with pdfplumber.open(file_path) as pdf:
            for i, page in enumerate(pdf.pages, start=1):
                text = page.extract_text()
                if text:
                    pages.append((i, text.strip()))
    except Exception as e:
        raise RuntimeError(f"Failed to extract pages from PDF: {e}")

    return pages


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> list[str]:
    """
    Split text into overlapping chunks for embedding.

    Args:
        text: The full text to split.
        chunk_size: Maximum characters per chunk.
        overlap: Number of overlapping characters between consecutive chunks.

    Returns:
        List of text chunks.
    """
    if not text or not text.strip():
        return []

    chunks = []
    start = 0
    text_len = len(text)

    while start < text_len:
        end = start + chunk_size

        # Try to break at a sentence boundary (period, newline) near the end
        if end < text_len:
            # Look backwards from `end` for a good break point
            break_point = text.rfind(".", start + chunk_size // 2, end)
            if break_point == -1:
                break_point = text.rfind("\n", start + chunk_size // 2, end)
            if break_point != -1:
                end = break_point + 1

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        # Move forward by chunk_size minus overlap
        start = end - overlap if end < text_len else text_len

    return chunks


def get_page_count(file_path: str) -> int:
    """Get the number of pages in a PDF file."""
    try:
        with pdfplumber.open(file_path) as pdf:
            return len(pdf.pages)
    except Exception:
        return 0


def get_file_size_mb(file_path: str) -> float:
    """Get file size in megabytes."""
    try:
        size_bytes = os.path.getsize(file_path)
        return round(size_bytes / (1024 * 1024), 2)
    except Exception:
        return 0.0
