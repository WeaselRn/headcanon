"""
Unit tests for Headcanon Media Pipeline & Narration Engine (Milestone 8).

Tests NarrationEngine and MediaPipeline for:
  - Narration text generation & sensory details
  - Image prompt generation
  - Ambient audio metadata generation (Forest, Castle, Dungeon)
  - Non-blocking execution & fallback resilience on image generation failures
  - Provenance tracking & StorageService upload integration
"""

from __future__ import annotations

import json
from unittest.mock import MagicMock

from app.engines.media_pipeline import (
    MediaPipeline,
    MediaPipelineResult,
)
from app.engines.narration_engine import NarrationEngine, NarrationResult
from app.world.scene import (
    Scene,
    SceneCharacterSummary,
    SceneEnvironment,
    SceneLocationSummary,
    SceneObjectSummary,
)


class StubAIClient:
    """Stub AI Client returning pre-configured JSON or string responses."""

    def __init__(self, response_map: dict[str, str] | None = None) -> None:
        self.response_map = response_map or {}

    def generate(self, prompt: str) -> str:
        for key, val in self.response_map.items():
            if key in prompt:
                return val
        return json.dumps(
            {
                "narration": "Morning sunlight fills the quiet room.",
                "sensory_details": ["sight", "sound"],
                "atmosphere": "Peaceful",
            }
        )


def create_sample_scene(location_name: str = "Hogwarts Library") -> Scene:
    return Scene(
        scene_id="scene_loc_library",
        universe_id="hp_001",
        timestamp="Day 1, 10:00",
        location=SceneLocationSummary(
            location_id="loc_library",
            name=location_name,
            description="A quiet research hall filled with dusty manuscripts.",
        ),
        narration="A quiet hall with dusty manuscripts.",
        characters=[
            SceneCharacterSummary(
                character_id="char_hermione",
                name="Hermione Granger",
                current_emotion="Focused",
            )
        ],
        objects=[
            SceneObjectSummary(
                object_id="obj_wand",
                name="Elder Wand",
                category="Weapon",
            )
        ],
        environment=SceneEnvironment(
            time_of_day="Morning",
            weather="Sunny",
            lighting="Bright",
        ),
    )


# ---------------------------------------------------------------------------
# NarrationEngine Tests
# ---------------------------------------------------------------------------


class TestNarrationEngine:
    def test_generate_narration_fallback_without_ai_client(self):
        engine = NarrationEngine()
        scene = create_sample_scene()

        res = engine.generate_narration(scene)
        assert isinstance(res, NarrationResult)
        assert res.scene_id == "scene_loc_library"
        assert "dusty manuscripts" in res.narration_text

    def test_generate_narration_with_ai_client(self):
        ai_resp = json.dumps(
            {
                "narration": "Sunlight streams across dusty bookshelves as Hermione studies.",
                "sensory_details": ["sight", "smell of parchment"],
                "atmosphere": "Studious",
            }
        )
        client = StubAIClient({"narration": ai_resp})
        engine = NarrationEngine(ai_client=client)
        scene = create_sample_scene()

        res = engine.generate_narration(scene)
        expected_narration = "Sunlight streams across dusty bookshelves as Hermione studies."
        assert res.narration_text == expected_narration
        assert res.atmosphere == "Studious"
        assert "sight" in res.sensory_details


# ---------------------------------------------------------------------------
# MediaPipeline Tests
# ---------------------------------------------------------------------------


class TestMediaPipeline:
    def test_generate_image_prompt_fallback(self):
        pipeline = MediaPipeline()
        scene = create_sample_scene()

        prompt = pipeline.generate_image_prompt(scene)
        assert prompt is not None
        assert "Illustration of Hogwarts Library" in prompt

    def test_generate_ambient_audio_metadata(self):
        pipeline = MediaPipeline()

        scene_forest = create_sample_scene("Forbidden Forest")
        meta_forest = pipeline.generate_ambient_audio_metadata(scene_forest)
        assert meta_forest.category == "Forest"
        assert "Birds" in meta_forest.sounds

        scene_castle = create_sample_scene("Great Hall")
        meta_castle = pipeline.generate_ambient_audio_metadata(scene_castle)
        assert meta_castle.category == "Castle"
        assert "Fireplace crackle" in meta_castle.sounds

    def test_process_scene_without_storage(self):
        pipeline = MediaPipeline()
        scene = create_sample_scene()

        res = pipeline.process_scene(scene)
        assert isinstance(res, MediaPipelineResult)
        assert res.success
        assert res.scene_id == "scene_loc_library"
        assert "dusty manuscripts" in res.narration_script
        assert res.ambient_audio is not None

    def test_process_scene_with_mock_storage_service(self):
        pipeline = MediaPipeline()
        scene = create_sample_scene()

        mock_storage = MagicMock()
        res = pipeline.process_scene(scene, storage_service=mock_storage)

        assert res.success
        assert len(res.assets_metadata) > 0
        # Verify upload was called for narration script and provenance
        assert mock_storage.upload.call_count >= 2

    def test_process_scene_failure_resilience(self):
        # Force illustration generation to raise an exception
        client = StubAIClient()
        pipeline = MediaPipeline(ai_client=client)
        pipeline.generate_illustration = MagicMock(side_effect=RuntimeError("Image server down"))

        scene = create_sample_scene()

        # Should NOT raise RuntimeError — must fail gracefully without illustration
        res = pipeline.process_scene(scene)

        assert res.success
        assert res.illustration_url is None
        assert res.narration_script != ""
