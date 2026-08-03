"""
StorageManager for Headcanon.

Coordinates repositories, storage paths, serialization, version metadata,
and export/import functionality across the persistence layer.
"""

from __future__ import annotations

import logging
import os
import shutil
import zipfile
from pathlib import Path

from app.repositories.exceptions import (
    InvalidStorageDataError,
    UniverseNotFoundError,
    WorldStateNotFoundError,
)
from app.repositories.snapshot_repository import SnapshotRepository
from app.repositories.universe_repository import UniverseRepository
from app.repositories.world_state_repository import WorldStateRepository
from app.world.universe import Universe
from app.world.world_state import WorldState

logger = logging.getLogger(__name__)


class StorageManager:
    """
    Coordinator for Headcanon persistence and storage operations.

    Responsibilities:
      - Coordinate UniverseRepository, WorldStateRepository, SnapshotRepository
      - Enforce storage directory structure
      - Handle full universe save/load operations (save_all, load_all)
      - Provide export and import of complete universe archives (.zip or folder)

    Storage Layout:
        {base_dir}/
            universes/
                {universe_id}/
                    universe.json
                    world_state.json
                    metadata.json
                    snapshots/
                    media/
                    provenance/

    Args:
        base_dir: Path to storage root directory.
    """

    def __init__(self, base_dir: Path | str) -> None:
        self.base_dir = Path(base_dir)
        self.universes_dir = self.base_dir / "universes"

        # Injected repositories sharing the same base directory
        self.universe_repo = UniverseRepository(self.base_dir)
        self.world_state_repo = WorldStateRepository(self.base_dir)
        self.snapshot_repo = SnapshotRepository(self.base_dir, self.world_state_repo)

    def initialize(self) -> None:
        """Ensure base storage directories exist on disk."""
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.universes_dir.mkdir(parents=True, exist_ok=True)
        logger.info("Initialized StorageManager at %s", self.base_dir)

    def save_all(self, universe: Universe, world_state: WorldState | None = None) -> None:
        """
        Atomically save Universe and its active WorldState.

        Args:
            universe: Universe model instance to save.
            world_state: Optional WorldState instance. If omitted, uses
                         universe.world_state if present.

        Raises:
            ValueError: If universe or world_state validation fails.
        """
        self.initialize()
        self.universe_repo.save_universe(universe)

        target_state = world_state or universe.world_state
        if target_state is not None:
            if target_state.universe_id != universe.metadata.id:
                raise ValueError(
                    f"WorldState universe_id '{target_state.universe_id}' does not match "
                    f"Universe ID '{universe.metadata.id}'."
                )
            self.world_state_repo.save(target_state)

        logger.info("save_all completed for universe '%s'", universe.metadata.id)

    def load_all(self, universe_id: str) -> tuple[Universe, WorldState]:
        """
        Load Universe and its active WorldState together.

        Args:
            universe_id: Unique universe identifier.

        Returns:
            Tuple of (Universe, WorldState).

        Raises:
            UniverseNotFoundError: If universe does not exist.
            WorldStateNotFoundError: If world_state.json is missing.
        """
        universe = self.universe_repo.load_universe(universe_id)
        try:
            world_state = self.world_state_repo.load(universe_id)
        except WorldStateNotFoundError:
            if universe.world_state is not None:
                world_state = universe.world_state
                self.world_state_repo.save(world_state)
            else:
                raise

        return universe, world_state

    def export(self, universe_id: str, export_path: str | Path) -> Path:
        """
        Package and export a complete universe directory into a .zip archive.

        Args:
            universe_id: ID of universe to export.
            export_path: Destination zip file path or directory.

        Returns:
            Path to the created export zip file.

        Raises:
            UniverseNotFoundError: If universe does not exist.
        """
        if not self.universe_repo.exists(universe_id):
            raise UniverseNotFoundError(f"Cannot export universe '{universe_id}': not found.")

        src_dir = self.universes_dir / universe_id
        dest = Path(export_path)

        if dest.is_dir():
            dest_zip = dest / f"{universe_id}.zip"
        else:
            dest_zip = dest if str(dest).endswith(".zip") else Path(f"{dest}.zip")

        dest_zip.parent.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(dest_zip, "w", zipfile.ZIP_DEFLATED) as z:
            for root, _dirs, files in os.walk(src_dir):
                for file in files:
                    full_path = Path(root) / file
                    arcname = full_path.relative_to(src_dir)
                    z.write(full_path, arcname=arcname)

        logger.info("Exported universe '%s' to %s", universe_id, dest_zip)
        return dest_zip

    def import_universe(self, import_path: str | Path) -> Universe:
        """
        Unpackage and import a universe from a .zip archive or directory into storage.

        Args:
            import_path: Path to zip file or uncompressed universe directory.

        Returns:
            Imported and validated Universe model instance.

        Raises:
            InvalidStorageDataError: If archive is corrupt or invalid.
        """
        self.initialize()
        path = Path(import_path)

        if not path.exists():
            raise FileNotFoundError(f"Import path '{import_path}' does not exist.")

        if path.is_file() and zipfile.is_zipfile(path):
            # Extract to temp directory first
            import tempfile

            with tempfile.TemporaryDirectory() as tmp_dir:
                tmp_path = Path(tmp_dir)
                with zipfile.ZipFile(path, "r") as z:
                    z.extractall(tmp_path)

                return self._import_from_dir(tmp_path)

        if path.is_dir():
            return self._import_from_dir(path)

        raise InvalidStorageDataError(
            f"Import path '{import_path}' is neither a zip file nor a directory."
        )

    def _import_from_dir(self, source_dir: Path) -> Universe:
        """Import universe directory into storage after validating models."""
        universe_file = source_dir / "universe.json"
        if not universe_file.exists():
            raise InvalidStorageDataError(
                f"Import directory '{source_dir}' missing 'universe.json'."
            )

        try:
            raw_universe = universe_file.read_text(encoding="utf-8")
            universe = Universe.model_validate_json(raw_universe)
        except Exception as exc:
            raise InvalidStorageDataError(
                f"Failed to validate imported universe.json: {exc}"
            ) from exc

        universe_id = universe.metadata.id
        target_dir = self.universes_dir / universe_id

        # Copy extracted directory to target storage location
        if target_dir.exists():
            shutil.rmtree(target_dir)

        shutil.copytree(source_dir, target_dir)

        # Validate world_state if present
        ws_file = target_dir / "world_state.json"
        if ws_file.exists():
            try:
                WorldState.model_validate_json(ws_file.read_text(encoding="utf-8"))
            except Exception as exc:
                logger.warning("Imported world_state.json is invalid: %s", exc)

        logger.info("Imported universe '%s' to %s", universe_id, target_dir)
        return universe
