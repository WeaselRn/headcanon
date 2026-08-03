"""
Repository exceptions for Headcanon persistence layer.

Defines explicit error types for repository operations.
"""

from __future__ import annotations


class RepositoryError(RuntimeError):
    """Base exception for repository and persistence errors."""


class UniverseNotFoundError(RepositoryError):
    """Raised when a requested Universe ID is not found in storage."""


class WorldStateNotFoundError(RepositoryError):
    """Raised when a requested World State is not found in storage."""


class SnapshotNotFoundError(RepositoryError):
    """Raised when a requested Snapshot ID is not found in storage."""


class InvalidStorageDataError(RepositoryError):
    """Raised when stored JSON data fails model validation or is corrupt."""
