"""
Unit tests for Headcanon persistence layer (Milestone 4).

Tests UniverseRepository, WorldStateRepository, SnapshotRepository, and
StorageManager for atomic save, load, delete, snapshot create/restore,
validation errors, and export/import operations.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from app.repositories.exceptions import (
    InvalidStorageDataError,
    SnapshotNotFoundError,
    UniverseNotFoundError,
    WorldStateNotFoundError,
)
from app.repositories.snapshot_repository import SnapshotRepository
from app.repositories.universe_repository import UniverseRepository
from app.repositories.world_state_repository import WorldStateRepository
from app.storage.storage_manager import StorageManager
from app.world.character import Character
from app.world.location import Location, LocationCategory
from app.world.snapshot import SnapshotSaveType
from app.world.timeline import Timeline, TimelineEvent, WorldTime
from app.world.universe import ImportSource, Universe, UniverseMetadata
from app.world.world_state import CharacterState, LocationState, WorldState

# ---------------------------------------------------------------------------
# Test Fixtures / Helpers
# ---------------------------------------------------------------------------

NOW = datetime(2026, 8, 4, 1, 0, 0, tzinfo=UTC)


def create_sample_universe(universe_id: str = "hp_test_001") -> Universe:
    """Construct a minimal valid Universe model for testing."""
    metadata = UniverseMetadata(
        id=universe_id,
        title="Harry Potter Test Universe",
        author="J. K. Rowling",
        source=ImportSource.CUSTOM,
        created_at=NOW,
    )
    harry = Character(
        id="char_harry",
        name="Harry Potter",
        description="The Boy Who Lived.",
    )
    hogwarts = Location(
        id="loc_hogwarts",
        name="Hogwarts Castle",
        description="Magical school.",
        category=LocationCategory.CASTLE,
    )
    sorting = TimelineEvent(
        id="evt_sorting",
        title="Sorting Ceremony",
        sequence=1,
        participants=["char_harry"],
        location="loc_hogwarts",
    )

    return Universe(
        metadata=metadata,
        characters=[harry],
        locations=[hogwarts],
        timeline=Timeline(events=[sorting]),
    )


def create_sample_world_state(universe_id: str = "hp_test_001") -> WorldState:
    """Construct a minimal valid WorldState model for testing."""
    char_states = {
        "char_harry": CharacterState(
            character_id="char_harry",
            location="loc_hogwarts",
            health="Healthy",
        )
    }
    loc_states = {
        "loc_hogwarts": LocationState(
            location_id="loc_hogwarts",
            occupants=["char_harry"],
        )
    }
    return WorldState(
        universe_id=universe_id,
        time=WorldTime(day=2, hour=14),
        characters=char_states,
        locations=loc_states,
        flags={"simulation_started": True},
    )


# ---------------------------------------------------------------------------
# UniverseRepository Tests
# ---------------------------------------------------------------------------


class TestUniverseRepository:
    def test_save_and_load_universe(self, tmp_path: Path):
        repo = UniverseRepository(tmp_path)
        uni = create_sample_universe("uni_001")

        repo.save_universe(uni)
        assert repo.exists("uni_001")

        loaded = repo.load_universe("uni_001")
        assert loaded.metadata.id == "uni_001"
        assert loaded.metadata.title == "Harry Potter Test Universe"
        assert len(loaded.characters) == 1
        assert loaded.characters[0].id == "char_harry"

    def test_exists(self, tmp_path: Path):
        repo = UniverseRepository(tmp_path)
        assert not repo.exists("non_existent")

        uni = create_sample_universe("uni_002")
        repo.save_universe(uni)
        assert repo.exists("uni_002")

    def test_delete(self, tmp_path: Path):
        repo = UniverseRepository(tmp_path)
        uni = create_sample_universe("uni_003")
        repo.save_universe(uni)
        assert repo.exists("uni_003")

        repo.delete("uni_003")
        assert not repo.exists("uni_003")

    def test_delete_non_existent_raises_not_found(self, tmp_path: Path):
        repo = UniverseRepository(tmp_path)
        with pytest.raises(UniverseNotFoundError):
            repo.delete("missing_uni")

    def test_load_non_existent_raises_not_found(self, tmp_path: Path):
        repo = UniverseRepository(tmp_path)
        with pytest.raises(UniverseNotFoundError):
            repo.load_universe("missing_uni")

    def test_list_and_list_metadata(self, tmp_path: Path):
        repo = UniverseRepository(tmp_path)
        uni1 = create_sample_universe("uni_a")
        uni2 = create_sample_universe("uni_b")

        repo.save_universe(uni1)
        repo.save_universe(uni2)

        uids = repo.list()
        assert uids == ["uni_a", "uni_b"]

        metas = repo.list_metadata()
        assert len(metas) == 2
        assert {m.id for m in metas} == {"uni_a", "uni_b"}

    def test_load_corrupt_json_raises_invalid_storage_data(self, tmp_path: Path):
        repo = UniverseRepository(tmp_path)
        uni = create_sample_universe("uni_corrupt")
        repo.save_universe(uni)

        # Corrupt universe.json
        uni_file = tmp_path / "universes" / "uni_corrupt" / "universe.json"
        uni_file.write_text("INVALID JSON content {", encoding="utf-8")

        with pytest.raises(InvalidStorageDataError):
            repo.load_universe("uni_corrupt")


# ---------------------------------------------------------------------------
# WorldStateRepository Tests
# ---------------------------------------------------------------------------


class TestWorldStateRepository:
    def test_save_and_load(self, tmp_path: Path):
        repo = WorldStateRepository(tmp_path)
        ws = create_sample_world_state("uni_ws_001")

        repo.save(ws)
        loaded = repo.load("uni_ws_001")
        assert loaded.universe_id == "uni_ws_001"
        assert loaded.time.day == 2
        assert loaded.characters["char_harry"].location == "loc_hogwarts"

    def test_update_and_latest(self, tmp_path: Path):
        repo = WorldStateRepository(tmp_path)
        ws = create_sample_world_state("uni_ws_002")
        repo.save(ws)

        # Update health and day
        updated_ws = ws.model_copy(
            update={"time": WorldTime(day=5, hour=10)}
        )
        returned_ws = repo.update("uni_ws_002", updated_ws)

        assert returned_ws.time.day == 5
        latest_ws = repo.latest("uni_ws_002")
        assert latest_ws.time.day == 5

    def test_load_missing_raises_not_found(self, tmp_path: Path):
        repo = WorldStateRepository(tmp_path)
        with pytest.raises(WorldStateNotFoundError):
            repo.load("non_existent_ws")

    def test_update_mismatched_universe_id_raises_value_error(self, tmp_path: Path):
        repo = WorldStateRepository(tmp_path)
        ws = create_sample_world_state("uni_a")

        with pytest.raises(ValueError, match="does not match"):
            repo.update("uni_b", ws)


# ---------------------------------------------------------------------------
# SnapshotRepository Tests
# ---------------------------------------------------------------------------


class TestSnapshotRepository:
    def test_create_and_load_snapshot(self, tmp_path: Path):
        snap_repo = SnapshotRepository(tmp_path)
        ws = create_sample_world_state("uni_snap_001")

        snap = snap_repo.create_snapshot(
            universe_id="uni_snap_001",
            world_state=ws,
            description="First test checkpoint",
            save_type=SnapshotSaveType.CHECKPOINT,
        )

        assert snap.universe_id == "uni_snap_001"
        assert snap.metadata.description == "First test checkpoint"
        assert snap.metadata.save_type == SnapshotSaveType.CHECKPOINT

        loaded = snap_repo.load_snapshot("uni_snap_001", snap.snapshot_id)
        assert loaded.snapshot_id == snap.snapshot_id
        assert loaded.world_state.time.day == ws.time.day

    def test_restore_snapshot(self, tmp_path: Path):
        ws_repo = WorldStateRepository(tmp_path)
        snap_repo = SnapshotRepository(tmp_path, world_state_repo=ws_repo)

        # Initial state at Day 2
        ws1 = create_sample_world_state("uni_restore_001")
        ws_repo.save(ws1)

        # Create snapshot of Day 2
        snap1 = snap_repo.create_snapshot("uni_restore_001", ws1, description="Day 2 Save")

        # Advance live WorldState to Day 10
        ws2 = ws1.model_copy(update={"time": WorldTime(day=10, hour=0)})
        ws_repo.save(ws2)
        assert ws_repo.load("uni_restore_001").time.day == 10

        # Restore Day 2 snapshot
        restored = snap_repo.restore_snapshot("uni_restore_001", snap1.snapshot_id)
        assert restored.time.day == 2
        # Check world_state.json file on disk is also updated
        assert ws_repo.load("uni_restore_001").time.day == 2

    def test_list_snapshots(self, tmp_path: Path):
        snap_repo = SnapshotRepository(tmp_path)
        ws = create_sample_world_state("uni_list_snaps")

        snap1 = snap_repo.create_snapshot("uni_list_snaps", ws, description="Snap 1")
        snap2 = snap_repo.create_snapshot("uni_list_snaps", ws, description="Snap 2")

        snaps = snap_repo.list_snapshots("uni_list_snaps")
        assert len(snaps) == 2
        snap_ids = {s.snapshot_id for s in snaps}
        assert snap_ids == {snap1.snapshot_id, snap2.snapshot_id}

    def test_load_non_existent_snapshot_raises_not_found(self, tmp_path: Path):
        snap_repo = SnapshotRepository(tmp_path)
        with pytest.raises(SnapshotNotFoundError):
            snap_repo.load_snapshot("uni_list_snaps", "missing_snap_id")


# ---------------------------------------------------------------------------
# StorageManager Tests
# ---------------------------------------------------------------------------


class TestStorageManager:
    def test_save_all_and_load_all(self, tmp_path: Path):
        mgr = StorageManager(tmp_path)
        uni = create_sample_universe("uni_mgr_001")
        ws = create_sample_world_state("uni_mgr_001")

        mgr.save_all(uni, ws)

        loaded_uni, loaded_ws = mgr.load_all("uni_mgr_001")
        assert loaded_uni.metadata.id == "uni_mgr_001"
        assert loaded_ws.universe_id == "uni_mgr_001"
        assert loaded_ws.characters["char_harry"].location == "loc_hogwarts"

    def test_export_and_import_universe(self, tmp_path: Path):
        mgr1 = StorageManager(tmp_path / "storage_a")
        uni = create_sample_universe("uni_export_001")
        ws = create_sample_world_state("uni_export_001")
        mgr1.save_all(uni, ws)

        # Create a snapshot before export
        mgr1.snapshot_repo.create_snapshot("uni_export_001", ws, description="Pre-export snapshot")

        # Export zip
        zip_path = tmp_path / "export.zip"
        result_zip = mgr1.export("uni_export_001", zip_path)
        assert result_zip.exists()

        # Import into storage_b
        mgr2 = StorageManager(tmp_path / "storage_b")
        imported_uni = mgr2.import_universe(result_zip)

        assert imported_uni.metadata.id == "uni_export_001"
        assert mgr2.universe_repo.exists("uni_export_001")

        loaded_uni, loaded_ws = mgr2.load_all("uni_export_001")
        assert loaded_uni.metadata.title == uni.metadata.title
        assert len(mgr2.snapshot_repo.list_snapshots("uni_export_001")) == 1

    def test_import_invalid_archive_raises(self, tmp_path: Path):
        mgr = StorageManager(tmp_path)
        fake_zip = tmp_path / "fake.zip"
        fake_zip.write_text("NOT A ZIP", encoding="utf-8")

        with pytest.raises(InvalidStorageDataError):
            mgr.import_universe(fake_zip)
