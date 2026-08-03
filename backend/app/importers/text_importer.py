"""
Plain Text Story Importer for Headcanon.

Imports and normalizes UTF-8 plain text files and raw text content.
"""

from __future__ import annotations

import os
import re

from app.importers.base import BaseStoryImporter
from app.importers.exceptions import (
    EmptyDocumentError,
    InvalidEncodingError,
    MissingFileError,
    UnsupportedFormatError,
)


class TextImporter(BaseStoryImporter):
    """
    Importer for Plain Text (.txt, .md, raw text) documents.

    Responsibilities:
      - Read UTF-8 plain text (file path, raw text string, bytes, or stream)
      - Auto-detect and handle UTF-8, UTF-8-SIG, and latin-1 encodings
      - Infer title and chapter structure
      - Normalize line endings and whitespace
      - Return clean UTF-8 text
    """

    def validate_source(self, source: str | os.PathLike | bytes) -> bool:
        """Validate text source path or content presence."""
        if isinstance(source, (str, os.PathLike)):
            path_str = str(source)
            # If path_str looks like a file path (ends with extension or contains path sep)
            if ("\n" not in path_str) and (
                os.path.sep in path_str
                or "/" in path_str
                or path_str.endswith((".txt", ".md", ".text"))
            ):
                if not os.path.exists(path_str):
                    raise MissingFileError(f"Text file not found: {path_str}")
                return True

            # If it's a raw string containing story text
            if len(path_str.strip()) > 0:
                return True
            raise EmptyDocumentError("Provided text string is empty.")

        if isinstance(source, bytes):
            if len(source.strip()) == 0:
                raise EmptyDocumentError("Provided bytes are empty.")
            return True

        if hasattr(source, "read"):
            return True

        raise UnsupportedFormatError(f"Unsupported Text source type: {type(source)}")

    def load(self, source: str | os.PathLike | bytes) -> str:
        """Load text content, attempting UTF-8, UTF-8-SIG, and latin-1 decoding."""
        if isinstance(source, (str, os.PathLike)):
            path_str = str(source)
            if ("\n" not in path_str) and (os.path.exists(path_str)):
                try:
                    with open(path_str, "rb") as f:
                        data = f.read()
                    return _decode_bytes(data)
                except Exception as exc:
                    if isinstance(
                        exc, (MissingFileError, InvalidEncodingError, EmptyDocumentError)
                    ):
                        raise
                    raise InvalidEncodingError(
                        f"Failed to read/decode text file '{path_str}': {exc}"
                    ) from exc

            # Raw text string
            return path_str

        if isinstance(source, bytes):
            return _decode_bytes(source)

        if hasattr(source, "read"):
            data = source.read()
            if isinstance(data, str):
                return data
            return _decode_bytes(data)

        raise UnsupportedFormatError("Invalid source type for Text load.")

    def extract(self, loaded_text: str) -> tuple[str, dict[str, str | int | None]]:
        """Extract text and metadata from loaded plain text."""
        if not loaded_text or not loaded_text.strip():
            raise EmptyDocumentError("Text document is empty.")

        lines = [line.strip() for line in loaded_text.splitlines() if line.strip()]
        first_line = lines[0] if lines else "Untitled Story"

        # Infer title from first line if short (<= 60 chars)
        title = first_line if len(first_line) <= 60 else first_line[:60] + "..."

        chapter_count = _count_text_chapters(loaded_text)

        metadata_dict: dict[str, str | int | None] = {
            "source_type": "txt",
            "title": title,
            "author": "Unknown",
            "language": "English",
            "chapter_count": chapter_count,
            "word_count": len(loaded_text.split()),
        }

        return loaded_text, metadata_dict


def _decode_bytes(data: bytes) -> str:
    """Attempt decoding bytes using UTF-8, UTF-8-SIG, and fallback to latin-1."""
    if not data:
        raise EmptyDocumentError("Input bytes are empty.")

    for encoding in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue

    raise InvalidEncodingError("Unable to decode input bytes with UTF-8 or latin-1 encodings.")


def _count_text_chapters(text: str) -> int:
    """Estimate chapter count in plain text document."""
    pattern = r"(?mi)^(?:Chapter|PART|Book)\s+(?:\d+|[IVXLCDM]+|[A-Z][a-z]+)"
    matches = re.findall(pattern, text)
    return len(matches) if matches else 1
