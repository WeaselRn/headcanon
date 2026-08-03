"""
PDF Story Importer for Headcanon.

Extracts text from PDF files using pypdf, preserving reading order and chapter
boundaries while stripping headers, footers, and page numbers.
"""

from __future__ import annotations

import io
import os
import re
from typing import Any

from pypdf import PdfReader

from app.importers.base import BaseStoryImporter
from app.importers.exceptions import (
    CorruptFileError,
    EmptyDocumentError,
    MissingFileError,
    UnsupportedFormatError,
)


class PDFImporter(BaseStoryImporter):
    """
    Importer for PDF documents.

    Responsibilities:
      - Read PDF via pypdf (file path, bytes, or stream)
      - Extract page text preserving reading order
      - Detect and remove repeated headers & footers across pages
      - Detect chapter boundaries
      - Extract PDF metadata (title, author)
      - Normalize whitespace and return clean UTF-8 text

    Does NOT perform OCR.  Scanned PDFs containing no text raise EmptyDocumentError.
    """

    def validate_source(self, source: str | os.PathLike | bytes) -> bool:
        """Validate PDF file existence and format signature."""
        if isinstance(source, (str, os.PathLike)):
            path_str = str(source)
            if not os.path.exists(path_str):
                raise MissingFileError(f"PDF file not found: {path_str}")
            if not path_str.lower().endswith(".pdf"):
                # Check magic bytes before rejecting
                try:
                    with open(path_str, "rb") as f:
                        header = f.read(5)
                        if not header.startswith(b"%PDF-"):
                            raise UnsupportedFormatError(f"File '{path_str}' is not a valid PDF.")
                except Exception as exc:
                    if isinstance(exc, (MissingFileError, UnsupportedFormatError)):
                        raise
                    raise UnsupportedFormatError(f"Cannot read file '{path_str}': {exc}") from exc
            return True

        if isinstance(source, bytes):
            if not source.startswith(b"%PDF-"):
                raise UnsupportedFormatError(
                    "Provided bytes do not represent a valid PDF (%PDF- header missing)."
                )
            return True

        if hasattr(source, "read"):
            return True

        raise UnsupportedFormatError(f"Unsupported PDF source type: {type(source)}")

    def load(self, source: str | os.PathLike | bytes) -> PdfReader:
        """Load and parse the PDF with pypdf."""
        try:
            if isinstance(source, (str, os.PathLike)):
                with open(str(source), "rb") as f:
                    data = f.read()
                return PdfReader(io.BytesIO(data))
            if isinstance(source, bytes):
                return PdfReader(io.BytesIO(source))
            if hasattr(source, "read"):
                data = source.read()
                return PdfReader(io.BytesIO(data))
            raise UnsupportedFormatError("Invalid source type for PDF load.")
        except Exception as exc:
            if isinstance(exc, (MissingFileError, UnsupportedFormatError)):
                raise
            raise CorruptFileError(f"Failed to parse PDF document: {exc}") from exc

    def extract(self, reader: PdfReader) -> tuple[str, dict[str, str | int | None]]:
        """Extract text per page, remove repeated headers/footers, and gather metadata."""
        if not reader.pages:
            raise EmptyDocumentError("PDF document has no pages.")

        page_texts: list[str] = []
        for _i, page in enumerate(reader.pages):
            try:
                txt = page.extract_text() or ""
                page_texts.append(txt)
            except Exception:
                page_texts.append("")

        # Check for empty document (e.g. scanned PDF)
        total_len = sum(len(t.strip()) for t in page_texts)
        if total_len == 0:
            raise EmptyDocumentError(
                "PDF document contains no extractable text (OCR may be required)."
            )

        # Detect repeated headers/footers
        cleaned_pages = _strip_repeated_headers_footers(page_texts)

        raw_text = "\n\n".join(p for p in cleaned_pages if p.strip())

        # Extract metadata
        meta: Any = reader.metadata or {}
        title = meta.title if hasattr(meta, "title") and meta.title else None
        author = meta.author if hasattr(meta, "author") and meta.author else None

        # Fallback title/author
        if not title:
            # Try to infer title from first line of text
            first_line = raw_text.split("\n")[0].strip()
            title = first_line[:50] if first_line else "Untitled PDF"

        chapter_count = _count_pdf_chapters(raw_text)

        metadata_dict: dict[str, str | int | None] = {
            "source_type": "pdf",
            "title": title,
            "author": author or "Unknown",
            "language": "English",
            "chapter_count": chapter_count,
            "page_count": len(reader.pages),
        }

        return raw_text, metadata_dict


def _strip_repeated_headers_footers(pages: list[str]) -> list[str]:
    """Identify and remove lines that repeat at page tops or bottoms across >= 30% of pages."""
    if len(pages) < 3:
        return pages

    top_lines: dict[str, int] = {}
    bottom_lines: dict[str, int] = {}

    for page in pages:
        lines = [line.strip() for line in page.splitlines() if line.strip()]
        if not lines:
            continue
        # First 2 lines
        for line in lines[:2]:
            if len(line) < 80:
                top_lines[line] = top_lines.get(line, 0) + 1
        # Last 2 lines
        for line in lines[-2:]:
            if len(line) < 80:
                bottom_lines[line] = bottom_lines.get(line, 0) + 1

    threshold = max(2, int(len(pages) * 0.3))
    headers_to_remove = {line for line, count in top_lines.items() if count >= threshold}
    footers_to_remove = {line for line, count in bottom_lines.items() if count >= threshold}

    cleaned_pages: list[str] = []
    for page in pages:
        lines = page.splitlines()
        filtered_lines = []
        for line in lines:
            s_line = line.strip()
            # Remove standalone page numbers like "12", "— 12 —", "Page 12"
            if re.match(r"^—?\s*\d+\s*—?$", s_line) or re.match(r"^Page\s+\d+$", s_line, re.I):
                continue
            if s_line in headers_to_remove or s_line in footers_to_remove:
                continue
            filtered_lines.append(line)
        cleaned_pages.append("\n".join(filtered_lines))

    return cleaned_pages


def _count_pdf_chapters(text: str) -> int:
    """Estimate chapter count based on standard chapter headings."""
    pattern = r"(?mi)^(?:Chapter|PART|Book)\s+(?:\d+|[IVXLCDM]+|[A-Z][a-z]+)"
    matches = re.findall(pattern, text)
    return len(matches) if matches else 1
