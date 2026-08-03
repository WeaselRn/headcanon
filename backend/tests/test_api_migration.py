"""
Unit tests for Headcanon Universe-Centric API Migration (Milestone 9).

Tests FastAPI routes for:
  - Universe API (/api/universes/import, GET /{id}, GET /, DELETE /{id})
  - Scene API (GET /api/scene, POST /api/scene/refresh)
  - Interaction API (POST /api/interact)
  - Simulation API (POST /api/simulate)
  - Media API (POST /api/media/generate, GET /api/media/{asset_id})
  - Storage API (POST /api/snapshot, GET /api/snapshots, POST /api/restore)
  - Clean HTTP error responses and schema validation
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import (
    get_ai_adapter,
    get_snapshot_repository,
    get_universe_repository,
    get_world_state_repository,
)
from app.main import app
from app.repositories.snapshot_repository import SnapshotRepository
from app.repositories.universe_repository import UniverseRepository
from app.repositories.world_state_repository import WorldStateRepository
from app.world.character import Character
from app.world.location import Location, LocationCategory
from app.world.timeline import WorldTime
from app.world.universe import ImportSource, Universe, UniverseMetadata
from app.world.world_state import CharacterState, LocationState, WorldState

NOW = datetime.now(tz=UTC)

# ---------------------------------------------------------------------------
# Test Fixtures & Helpers
# ---------------------------------------------------------------------------


class StubAIAdapter:
    """Stub AI adapter for UniverseBuilder / engines in API tests."""

    def generate(self, prompt: str) -> str:
        if "extract_characters" in prompt:
            return json.dumps(
                {
                    "characters": [
                        {
                            "id": "char_hermione",
                            "name": "Hermione Granger",
                            "personality": ["Logical"],
                        }
                    ]
                }
            )
        if "extract_locations" in prompt:
            return json.dumps(
                {
                    "locations": [
                        {
                            "id": "loc_library",
                            "name": "Hogwarts Library",
                            "description": "Quiet hall.",
                        }
                    ]
                }
            )
        if "extract_objects" in prompt:
            return json.dumps({"objects": []})
        if "extract_events" in prompt:
            return json.dumps({"events": []})
        if "extract_rules" in prompt:
            return json.dumps({"rules": []})
        if "extract_relationships" in prompt:
            return json.dumps({"relationships": []})
        if "merge_duplicates" in prompt:
            return prompt
        if "build_knowledge_graph" in prompt:
            return json.dumps({"nodes": [], "edges": []})
        if "initialize_world" in prompt:
            return json.dumps({"world_state": {}})
        return "{}"


def create_test_universe() -> Universe:
    meta = UniverseMetadata(
        id="hp_test_001",
        title="Harry Potter Test",
        author="J. K. Rowling",
        source=ImportSource.CUSTOM,
        created_at=NOW,
    )
    hermione = Character(id="char_hermione", name="Hermione Granger")
    library = Location(
        id="loc_library",
        name="Hogwarts Library",
        description="Quiet research hall.",
        category=LocationCategory.ROOM,
    )
    return Universe(
        metadata=meta,
        characters=[hermione],
        locations=[library],
    )


def create_test_world_state() -> WorldState:
    char_states = {
        "char_hermione": CharacterState(character_id="char_hermione", location="loc_library")
    }
    loc_states = {
        "loc_library": LocationState(location_id="loc_library", occupants=["char_hermione"])
    }
    return WorldState(
        universe_id="hp_test_001",
        time=WorldTime(day=1, hour=10),
        characters=char_states,
        locations=loc_states,
    )


@pytest.fixture
def api_client(tmp_path: Path):
    """FastAPI TestClient with overridden repository dependencies using temp storage."""
    uni_repo = UniverseRepository(base_dir=tmp_path)
    ws_repo = WorldStateRepository(base_dir=tmp_path)
    snap_repo = SnapshotRepository(base_dir=tmp_path, world_state_repo=ws_repo)

    # Save a test universe and world state into storage
    uni = create_test_universe()
    ws = create_test_world_state()
    uni_repo.save_universe(uni)
    ws_repo.save(ws)

    app.dependency_overrides[get_universe_repository] = lambda: uni_repo
    app.dependency_overrides[get_world_state_repository] = lambda: ws_repo
    app.dependency_overrides[get_snapshot_repository] = lambda: snap_repo
    app.dependency_overrides[get_ai_adapter] = lambda: StubAIAdapter()

    client = TestClient(app)
    yield client

    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Universe API Tests
# ---------------------------------------------------------------------------


class TestUniverseAPI:
    def test_import_universe_text(self, api_client: TestClient):
        payload = {
            "source_type": "text",
            "text": "Harry Potter walked into the Hogwarts Library. Hermione was reading a book.",
            "title": "Harry Potter Import Test",
            "author": "J. K. Rowling",
        }
        res = api_client.post("/api/universes/import", json=payload)
        assert res.status_code == 201
        data = res.json()
        assert "universe_id" in data
        assert data["title"] == "Harry Potter Import Test"
        assert data["status"] == "completed"

    def test_get_universe_metadata(self, api_client: TestClient):
        res = api_client.get("/api/universes/hp_test_001")
        assert res.status_code == 200
        data = res.json()
        assert data["universe_id"] == "hp_test_001"
        assert data["title"] == "Harry Potter Test"

    def test_get_universe_not_found(self, api_client: TestClient):
        res = api_client.get("/api/universes/non_existent_id")
        assert res.status_code == 404
        assert "not found" in res.json()["error"]

    def test_list_universes(self, api_client: TestClient):
        res = api_client.get("/api/universes")
        assert res.status_code == 200
        data = res.json()
        assert "universes" in data
        assert len(data["universes"]) >= 1

    def test_delete_universe(self, api_client: TestClient):
        res = api_client.delete("/api/universes/hp_test_001")
        assert res.status_code == 204


# ---------------------------------------------------------------------------
# Scene API Tests
# ---------------------------------------------------------------------------


class TestSceneAPI:
    def test_get_scene(self, api_client: TestClient):
        res = api_client.get("/api/scene?universe_id=hp_test_001")
        assert res.status_code == 200
        data = res.json()
        assert "scene" in data
        assert data["scene"]["location"]["location_id"] == "loc_library"

    def test_refresh_scene(self, api_client: TestClient):
        payload = {"universe_id": "hp_test_001", "location_id": "loc_library"}
        res = api_client.post("/api/scene/refresh", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["scene"]["location"]["name"] == "Hogwarts Library"


# ---------------------------------------------------------------------------
# Interaction API Tests
# ---------------------------------------------------------------------------


class TestInteractionAPI:
    def test_process_interaction(self, api_client: TestClient):
        payload = {
            "universe_id": "hp_test_001",
            "user_input": "Talk to Hermione",
        }
        res = api_client.post("/api/interact", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert "interaction_result" in data
        assert data["interaction_result"]["action"] == "talk"
        assert data["interaction_result"]["target"] == "char_hermione"


# ---------------------------------------------------------------------------
# Simulation API Tests
# ---------------------------------------------------------------------------


class TestSimulationAPI:
    def test_run_simulation(self, api_client: TestClient):
        interaction_res = {
            "interaction_id": "int_001",
            "action": "wait",
            "narration": "You wait as time passes.",
            "scene": {
                "scene_id": "scene_loc_library",
                "universe_id": "hp_test_001",
                "location": {"location_id": "loc_library", "name": "Library"},
            },
            "pending_world_effects": [{"type": "advance_time", "hours": 2}],
            "success": True,
        }
        payload = {
            "universe_id": "hp_test_001",
            "interaction_result": interaction_res,
        }
        res = api_client.post("/api/simulate", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert "simulation_result" in data
        assert "world_state" in data
        assert data["world_state"]["time"]["hour"] == 12  # 10 + 2 = 12


# ---------------------------------------------------------------------------
# Media API Tests
# ---------------------------------------------------------------------------


class TestMediaAPI:
    def test_generate_media(self, api_client: TestClient):
        scene_payload = {
            "scene_id": "scene_loc_library",
            "universe_id": "hp_test_001",
            "location": {
                "location_id": "loc_library",
                "name": "Hogwarts Library",
                "description": "Quiet hall.",
            },
        }
        payload = {"universe_id": "hp_test_001", "scene": scene_payload}
        res = api_client.post("/api/media/generate", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert "result" in data
        assert data["result"]["scene_id"] == "scene_loc_library"

    def test_get_asset_metadata(self, api_client: TestClient):
        res = api_client.get("/api/media/asset_img_12345")
        assert res.status_code == 200
        data = res.json()
        assert data["asset_metadata"]["asset_id"] == "asset_img_12345"


# ---------------------------------------------------------------------------
# Storage / Snapshot API Tests
# ---------------------------------------------------------------------------


class TestStorageAPI:
    def test_snapshot_lifecycle(self, api_client: TestClient):
        # 1. Create Snapshot
        snap_req = {"universe_id": "hp_test_001", "description": "Test Snapshot"}
        res1 = api_client.post("/api/snapshot", json=snap_req)
        assert res1.status_code == 200
        snap_data = res1.json()["snapshot"]
        snap_id = snap_data["snapshot_id"]

        # 2. List Snapshots
        res2 = api_client.get("/api/snapshots?universe_id=hp_test_001")
        assert res2.status_code == 200
        snaps_list = res2.json()["snapshots"]
        assert len(snaps_list) >= 1

        # 3. Restore Snapshot
        restore_req = {"universe_id": "hp_test_001", "snapshot_id": snap_id}
        res3 = api_client.post("/api/restore", json=restore_req)
        assert res3.status_code == 200
        assert res3.json()["snapshot"]["snapshot_id"] == snap_id
