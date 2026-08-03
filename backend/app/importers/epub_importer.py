"""
EPUB Story Importer for Headcanon.

Extracts text from EPUB ebooks while preserving chapter structure and stripping
HTML markup and navigation elements.
"""

from __future__ import annotations

import io
import os
import zipfile

import ebooklib
from bs4 import BeautifulSoup
from ebooklib import epub

from app.importers.base import BaseStoryImporter
from app.importers.exceptions import (
    CorruptFileError,
    EmptyDocumentError,
    MissingFileError,
    UnsupportedFormatError,
)


class EPUBImporter(BaseStoryImporter):
    """
    Importer for EPUB documents.

    Responsibilities:
      - Read EPUB files via ebooklib (file path, bytes, or stream)
      - Preserve chapter ordering from spine
      - Ignore navigation, TOC, and metadata pages
      - Strip HTML tags while preserving headings and paragraph boundaries
      - Extract metadata (title, author, language)
      - Return clean UTF-8 text
    """

    def validate_source(self, source: str | io.BytesIO | bytes) -> bool:
        """Validate that source exists and is a valid EPUB zip archive."""
        if isinstance(source, (str, os.PathLike)):
            path_str = str(source)
            if not os.path.exists(path_str):
                raise MissingFileError(f"EPUB file not found: {path_str}")
            if not zipfile.is_zipfile(path_str):
                raise UnsupportedFormatError(f"File '{path_str}' is not a valid zip/EPUB file.")
            return True

        if isinstance(source, bytes):
            if not source.startswith(b"PK\x03\x04"):
                raise UnsupportedFormatError("Bytes do not represent a valid ZIP/EPUB archive.")
            return True

        if hasattr(source, "read"):
            return True

        raise UnsupportedFormatError(f"Unsupported EPUB source type: {type(source)}")

    def load(self, source: str | io.BytesIO | bytes) -> epub.EpubBook:
        """Load and parse EPUB using ebooklib."""
        opts = {"ignore_ncx": True}
        try:
            if isinstance(source, (str, os.PathLike)):
                return epub.read_epub(str(source), options=opts)
            if isinstance(source, bytes):
                return epub.read_epub(io.BytesIO(source), options=opts)
            if hasattr(source, "read"):
                data = source.read()
                return epub.read_epub(io.BytesIO(data), options=opts)
            raise UnsupportedFormatError("Invalid source type for EPUB load.")
        except Exception as exc:
            if isinstance(exc, (MissingFileError, UnsupportedFormatError)):
                raise
            raise CorruptFileError(f"Failed to parse EPUB document: {exc}") from exc

    def extract(self, book: epub.EpubBook) -> tuple[str, dict[str, str | int | None]]:
        """Extract text content from spine items and extract Dublin Core metadata."""
        # Metadata extraction
        title_meta = book.get_metadata("DC", "title")
        title = str(title_meta[0][0]) if title_meta and title_meta[0] else "Untitled EPUB"

        creator_meta = book.get_metadata("DC", "creator")
        author = str(creator_meta[0][0]) if creator_meta and creator_meta[0] else "Unknown"

        lang_meta = book.get_metadata("DC", "language")
        language = str(lang_meta[0][0]) if lang_meta and lang_meta[0] else "English"

        chapter_texts: list[str] = []

        # Iterate document items in spine order
        for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
            name = item.get_name().lower()
            # Ignore TOC / nav files
            if any(k in name for k in ("nav.xhtml", "toc.xhtml", "cover.xhtml", "title.xhtml")):
                continue

            content_bytes = item.get_content()
            if not content_bytes:
                continue

            # Convert HTML to structured text
            soup = BeautifulSoup(content_bytes, "html.parser")

            # Remove navigation, script, style tags
            for elem in soup(["script", "style", "nav", "header", "footer"]):
                elem.decompose()

            text = _html_to_text(soup)
            if text.strip():
                chapter_texts.append(text.strip())

        if not chapter_texts:
            raise EmptyDocumentError("EPUB document contains no extractable story text.")

        raw_text = "\n\n".join(chapter_texts)

        metadata_dict: dict[str, str | int | None] = {
            "source_type": "epub",
            "title": title,
            "author": author,
            "language": language,
            "chapter_count": len(chapter_texts),
        }

        return raw_text, metadata_dict


def _html_to_text(soup: BeautifulSoup) -> str:
    """Convert HTML DOM to structured plain text preserving headings and paragraphs."""
    lines: list[str] = []

    for elem in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "p", "div"]):
        txt = elem.get_text().strip()
        if not txt:
            continue
        if elem.name.startswith("h"):
            lines.append(f"\n\n{txt}\n\n")
        else:
            lines.append(txt)

    if not lines:
        return soup.get_text().strip()

    return "\n\n".join(lines)
