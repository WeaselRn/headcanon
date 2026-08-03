"""
Media Pipeline for Headcanon.

Converts Scene models into multimedia assets (illustrations, narration, ambient audio metadata)
and stores them with complete metadata and provenance.

Media generation is non-blocking and optional — failure to generate an asset will never
corrupt the WorldState or interrupt gameplay.

Reference: docs/engines/10_media_pipeline.md, docs/storage/03_media_library.md
"""

from __future__ import annotations

import json
import logging
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from app.engines.narration_engine import NarrationEngine
from app.models.provenance import Provenance
from app.services.storage_service import StorageService
from app.world.scene import Scene, SceneMediaAssets

logger = logging.getLogger(__name__)

_PROMPT_DIR = Path(__file__).parent.parent / "prompts" / "media"


class AmbientAudioMetadata(BaseModel, frozen=True):
    """
    Structured metadata describing ambient soundscapes.

    Does NOT generate binary audio files — only structural audio tags.
    """

    category: str = Field(default="General")
    sounds: list[str] = Field(default_factory=list)


class AssetMetadata(BaseModel, frozen=True):
    """
    Metadata record for a generated media asset.
    """

    asset_id: str = Field(min_length=1)
    universe_id: str = Field(min_length=1)
    world_state_version: str | None = None
    scene_id: str = Field(min_length=1)
    generation_time: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    prompt_version: str = "1.0"
    model_used: str = "gemini-2.5-flash"
    storage_location: str | None = None
    provenance: Provenance | None = None


class MediaPipelineResult(BaseModel, frozen=True):
    """
    Structured outcome of media pipeline execution.
    """

    scene_id: str = Field(min_length=1)
    illustration_url: str | None = None
    narration_script: str = ""
    ambient_audio: AmbientAudioMetadata | None = None
    assets_metadata: list[AssetMetadata] = Field(default_factory=list)
    media_assets: SceneMediaAssets = Field(default_factory=SceneMediaAssets)
    success: bool = True
    error_message: str | None = None


class MediaPipeline:
    """
    The multimedia generation pipeline for Headcanon.

    Responsibilities:
      - Receive Scene object
      - Generate scene illustration prompt & image (or gracefully skip on failure)
      - Generate narration via NarrationEngine
      - Generate structured ambient audio metadata
      - Upload generated assets to StorageService with Provenance records
      - Return MediaPipelineResult with media asset URLs

    Args:
        ai_client: Optional injected AI client.
        narration_engine: Optional NarrationEngine instance.
        prompt_dir: Path to media prompt directory.
    """

    def __init__(
        self,
        ai_client: Any = None,
        narration_engine: NarrationEngine | None = None,
        prompt_dir: Path = _PROMPT_DIR,
    ) -> None:
        self.ai_client = ai_client
        self.narration_engine = narration_engine or NarrationEngine(ai_client, prompt_dir)
        self.prompt_dir = prompt_dir
        self._prompts: dict[str, str] = {}
        self._load_prompts()

    def _load_prompts(self) -> None:
        """Pre-load media prompt templates."""
        if self.prompt_dir.exists():
            for file in self.prompt_dir.glob("*.txt"):
                self._prompts[file.name] = file.read_text(encoding="utf-8")

    def process_scene(
        self,
        scene: Scene,
        storage_service: StorageService | None = None,
    ) -> MediaPipelineResult:
        """
        Execute media pipeline for a Scene.

        Pipeline steps:
          1. Generate narration via NarrationEngine
          2. Generate image prompt & illustration (graceful fallback if failed)
          3. Generate ambient audio metadata
          4. Record Provenance & AssetMetadata
          5. Upload assets to StorageService if provided
          6. Return MediaPipelineResult

        Args:
            scene: Input Scene model.
            storage_service: Optional StorageService for Backblaze persistence.

        Returns:
            MediaPipelineResult with media asset URLs and metadata.
        """
        now = datetime.now(tz=UTC)
        assets_metadata: list[AssetMetadata] = []
        uploaded_locations: list[str] = []

        # 1. Generate Narration
        narration_res = self.narration_engine.generate_narration(scene)
        narration_script = narration_res.narration_text

        # 2. Generate Image Prompt & Illustration
        illustration_url = None
        image_prompt = self.generate_image_prompt(scene)
        if image_prompt:
            try:
                illustration_url = self.generate_illustration(image_prompt, scene)
            except Exception as exc:
                logger.warning(
                    "Illustration generation failed for scene %s: %s", scene.scene_id, exc
                )

        # 3. Generate Ambient Audio Metadata
        ambient_audio = self.generate_ambient_audio_metadata(scene)

        # 4. Storage Upload & Asset Metadata / Provenance
        if storage_service is not None:
            try:
                prefix = f"universes/{scene.universe_id}/media/{scene.scene_id}/"

                # Upload narration script
                narr_key = f"{prefix}narration.txt"
                storage_service.upload(narr_key, narration_script.encode("utf-8"), "text/plain")
                uploaded_locations.append(narr_key)

                # Record Narration Asset Metadata
                assets_metadata.append(
                    AssetMetadata(
                        asset_id=f"asset_narr_{uuid.uuid4().hex[:6]}",
                        universe_id=scene.universe_id,
                        world_state_version=scene.metadata.world_state_version,
                        scene_id=scene.scene_id,
                        generation_time=now,
                        model_used="gemini-2.5-flash",
                        storage_location=narr_key,
                    )
                )

                # Record Image Asset Metadata if available
                if illustration_url:
                    img_key = f"{prefix}illustration.png"
                    uploaded_locations.append(img_key)
                    assets_metadata.append(
                        AssetMetadata(
                            asset_id=f"asset_img_{uuid.uuid4().hex[:6]}",
                            universe_id=scene.universe_id,
                            world_state_version=scene.metadata.world_state_version,
                            scene_id=scene.scene_id,
                            generation_time=now,
                            model_used="gemini-2.5-flash",
                            storage_location=img_key,
                        )
                    )

                # Build Provenance Record
                prov = Provenance(
                    execution_id=scene.scene_id,
                    pipeline_version="1.0",
                    models_used=["gemini-2.5-flash"],
                    started_at=now,
                    completed_at=datetime.now(tz=UTC),
                    assets_generated=[
                        m.storage_location for m in assets_metadata if m.storage_location
                    ],
                    status="completed",
                    storage_locations=uploaded_locations,
                )

                prov_key = f"{prefix}provenance.json"
                storage_service.upload(
                    prov_key, prov.model_dump_json().encode("utf-8"), "application/json"
                )
            except Exception as exc:
                logger.error("Storage upload failed in MediaPipeline: %s", exc)

        media_assets = SceneMediaAssets(
            illustration_url=illustration_url,
            narration_audio_url=None,
            ambient_audio_url=None,
        )

        return MediaPipelineResult(
            scene_id=scene.scene_id,
            illustration_url=illustration_url,
            narration_script=narration_script,
            ambient_audio=ambient_audio,
            assets_metadata=assets_metadata,
            media_assets=media_assets,
            success=True,
        )

    def generate_image_prompt(self, scene: Scene) -> str | None:
        """Generate a detailed visual prompt describing the scene."""
        if self.ai_client is None or "scene_image.txt" not in self._prompts:
            # Fallback visual description
            return (
                f"Illustration of {scene.location.name}. {scene.location.description}. "
                f"Time: {scene.environment.time_of_day or 'Day'}, "
                f"Weather: {scene.environment.weather or 'Clear'}."
            )

        template = self._prompts["scene_image.txt"]
        visible_chars = ", ".join(c.name for c in scene.characters) or "None"
        visible_objs = ", ".join(o.name for o in scene.objects) or "None"

        prompt = (
            template.replace("{location_name}", scene.location.name)
            .replace("{location_description}", scene.location.description)
            .replace("{time_of_day}", scene.environment.time_of_day or "Day")
            .replace("{weather}", scene.environment.weather or "Clear")
            .replace("{visible_characters}", visible_chars)
            .replace("{visible_objects}", visible_objs)
        )

        try:
            return self.ai_client.generate(prompt).strip()
        except Exception as exc:
            logger.warning("Failed to generate image prompt via LLM: %s", exc)
            return None

    def generate_illustration(self, image_prompt: str, scene: Scene) -> str | None:
        """
        Generate illustration image URL.

        Non-blocking: if image generation fails, returns None.
        """
        if self.ai_client is None:
            return None
        # Placeholder / stub image URL generation for testing & dev
        return f"https://storage.headcanon.ai/media/{scene.universe_id}/{scene.scene_id}_illustration.png"

    def generate_ambient_audio_metadata(self, scene: Scene) -> AmbientAudioMetadata:
        """
        Generate structured ambient soundscape metadata.

        Does NOT generate audio files.
        """
        category = "General"
        sounds = ["Background noise"]

        loc_name = scene.location.name.lower()
        if "forest" in loc_name or "woods" in loc_name:
            category = "Forest"
            sounds = ["Birds", "Wind", "Leaves rustling"]
        elif "hall" in loc_name or "castle" in loc_name or "room" in loc_name:
            category = "Castle"
            sounds = ["Fireplace crackle", "Distant footsteps", "Echoes"]
        elif "dungeon" in loc_name or "cave" in loc_name:
            category = "Dungeon"
            sounds = ["Dripping water", "Chains clanking", "Drafty wind"]

        if self.ai_client is not None and "ambient_audio.txt" in self._prompts:
            template = self._prompts["ambient_audio.txt"]
            prompt = template.replace("{location_name}", scene.location.name).replace(
                "{location_description}", scene.location.description
            )
            try:
                raw_res = self.ai_client.generate(prompt)
                data = _parse_json(raw_res)
                cat = str(data.get("category", category))
                snd = data.get("sounds", sounds)
                return AmbientAudioMetadata(
                    category=cat,
                    sounds=snd if isinstance(snd, list) else sounds,
                )
            except Exception as exc:
                logger.warning("Ambient audio LLM generation failed: %s", exc)

        return AmbientAudioMetadata(category=category, sounds=sounds)


def _parse_json(raw: str) -> dict[str, Any]:
    text = raw.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        text = "\n".join(lines[1:-1]).strip()
    return json.loads(text, strict=False)
