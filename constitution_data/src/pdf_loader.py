import os
import re
from typing import List

try:
    import fitz  # PyMuPDF
except Exception:
    fitz = None


def load_text(path: str) -> str:
    """Load text from a single file (PDF, TXT, or MD)."""
    ext = os.path.splitext(path)[1].lower()
    if ext in [".txt", ".md"]:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    if ext in [".pdf"]:
        if fitz is None:
            raise RuntimeError("PyMuPDF (fitz) not installed. pip install pymupdf")
        doc = fitz.open(path)
        texts = []
        for i in range(len(doc)):
            page = doc.load_page(i)
            texts.append(page.get_text("text"))
        doc.close()
        return "\n".join(texts)
    raise ValueError(f"Unsupported file extension: {ext}")


def load_multiple_texts(paths: List[str]) -> str:
    """Load and combine text from multiple files."""
    combined = []
    for path in paths:
        if not os.path.exists(path):
            print(f"Warning: File not found: {path}")
            continue
        print(f"Loading: {path}", os.getcwd())
        text = load_text(path)
        combined.append(text)
    return "\n\n".join(combined)


def get_pdf_files_from_directory(directory: str) -> List[str]:
    """Get all PDF files from a directory, sorted alphabetically."""
    print(os.getcwd())
    if not os.path.isdir(directory):
        raise ValueError(f"Not a directory: {directory}")
    pdf_files = []
    for filename in sorted(os.listdir(directory)):
        if filename.lower().endswith('.pdf'):
            pdf_files.append(os.path.join(directory, filename))
    return pdf_files
