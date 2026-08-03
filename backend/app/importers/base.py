"""
Abstract base class and common cleaning utilities for Headcanon story importers.

Every importer implements the same public interface:
  - validate_source(...)
  - load(...)
  - extract(...)
  - clean(...)
  - import_story(...)
"""

from __future__ import annotations

import re
import unicodedata
from abc import ABC, abstractmethod
from typing import Any

from app.importers.exceptions import EmptyDocumentError
from app.models.document import StoryDocument


def clean_text(raw_text: str) -> str:
    """
    Apply standard Headcanon text cleaning rules to raw story text.

    Normalizes:
      * Unicode characters (NFKC)
      * Smart/curly double quotes („ “ ”) -> standard double quote (")
      * Smart/curly single quotes & apostrophes (‘ ’ ‚) -> standard single quote (')
      * Unicode dashes (em-dash —, en-dash –) -> standard dash representation
      * Line endings (\r\n or \r -> \n)
      * Consecutive blank lines (collapses 4+ blank lines to max 2)
      * Horizontal whitespace within lines (collapses multiple spaces to 1)

    Preserves:
      * Dialogue and quotation marks
      * Narrative text
      * Chapter headings and paragraph structure

    Does NOT:
      * Summarize
      * Rewrite story text
      * Remove narrative content
    """
    if not raw_text:
        return ""

    text = raw_text

    # 1. Unicode normalization (NFKC)
    text = unicodedata.normalize("NFKC", text)

    # 2. Normalize Windows/Mac line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # 3. Strip control characters (keep \n and \t)
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)

    # 4. Normalize curly quotes and apostrophes
    text = re.sub(r"[“”«»„]", '"', text)
    text = re.sub(r"[‘’`‚]", "'", text)

    # 5. Normalize dashes (en-dash and em-dash to standard em-dash with spacing)
    text = text.replace("—", " — ").replace("–", " – ")
    text = re.sub(r" {2,}— {2,}", " — ", text)

    # 6. Remove trailing whitespace on each line
    text = re.sub(r"[ \t]+$", "", text, flags=re.MULTILINE)

    # 7. Collapse multiple horizontal spaces (preserve single spaces)
    text = re.sub(r"(?<!\n)[ \t]{2,}", " ", text)

    # 8. Collapse 4+ consecutive newlines into double blank lines (\n\n\n)
    text = re.sub(r"\n{4,}", "\n\n\n", text)

    return text.strip()


class BaseStoryImporter(ABC):
    """
    Abstract base class for all Headcanon story importers.

    Subclasses must implement validate_source, load, and extract.
    The import_story method orchestrates the full pipeline.
    """

    @abstractmethod
    def validate_source(self, source: Any) -> bool:
        """
        Validate that the source exists, is accessible, and has a supported format.

        Raises:
            MissingFileError, UnsupportedFormatError, etc. if invalid.
        """

    @abstractmethod
    def load(self, source: Any) -> Any:
        """
        Load the raw input data from the source (read file bytes, fetch URL, etc.).

        Raises:
            CorruptFileError, NetworkImportError, etc. if loading fails.
        """

    @abstractmethod
    def extract(self, loaded_data: Any) -> tuple[str, dict[str, Any]]:
        """
        Extract raw text and metadata dictionary from loaded data.

        Returns:
            Tuple of (raw_text, metadata_dict).

        Raises:
            EmptyDocumentError, ParsingFailureError, etc. if extraction fails.
        """

    def clean(self, raw_text: str) -> str:
        """
        Apply text cleaning and normalization rules to extracted raw text.

        Returns:
            Cleaned UTF-8 string.
        """
        return clean_text(raw_text)

    def import_story(self, source: Any) -> StoryDocument:
        """
        Orchestrate the complete import pipeline:
          1. validate_source
          2. load
          3. extract
          4. clean
          5. construct and return StoryDocument

        Returns:
            Fully populated StoryDocument model instance.

        Raises:
            StoryImportError subclasses on any failure.
        """
        self.validate_source(source)
        loaded_data = self.load(source)
        raw_text, metadata = self.extract(loaded_data)

        if not raw_text or not raw_text.strip():
            raise EmptyDocumentError("Document contains no extractable text.")

        cleaned = self.clean(raw_text)

        if not cleaned.strip():
            raise EmptyDocumentError("Cleaned document text is empty.")

        source_type = str(metadata.get("source_type", "unknown"))
        title = str(metadata.get("title", "Untitled"))
        author = metadata.get("author") or "Unknown"
        language = metadata.get("language") or "English"
        chapter_count = metadata.get("chapter_count")

        return StoryDocument(
            source_type=source_type,
            title=title,
            author=author,
            language=language,
            chapter_count=chapter_count,
            raw_text=raw_text,
            cleaned_text=cleaned,
            metadata=metadata,
        )
