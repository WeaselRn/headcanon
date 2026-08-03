"""
Exceptions for Headcanon story importers.

Defines explicit exception types for all story import failure modes as specified
in docs/error_handling.md and the Milestone 3 specification.
"""

from __future__ import annotations


class StoryImportError(RuntimeError):
    """Base exception for all story import errors."""


class UnsupportedFormatError(StoryImportError):
    """Raised when the input file extension, magic bytes, or URL format is unsupported."""


class CorruptFileError(StoryImportError):
    """Raised when an input PDF, EPUB, or archive is corrupted or unreadable."""


class MissingFileError(StoryImportError):
    """Raised when the specified input file path does not exist."""


class InvalidEncodingError(StoryImportError):
    """Raised when input text cannot be decoded as UTF-8 or supported text encoding."""


class EmptyDocumentError(StoryImportError):
    """Raised when an imported document contains no extractable text."""


class NetworkImportError(StoryImportError):
    """Raised when an HTTP request fails during web import (404, connection failure, timeout)."""


class ParsingFailureError(StoryImportError):
    """Raised when structural HTML/DOM parsing fails to locate readable story content."""
