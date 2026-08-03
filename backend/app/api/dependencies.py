"""
Dependency injection definitions for Headcanon API.

Registers repositories, storage managers, and engines for Universe, Scene,
Interaction, Simulation, Media, and Storage APIs.

Reference: docs/runtime_pipeline.md
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from fastapi import Depends

from app.config.settings import Settings, get_settings
from app.engines.character_engine import CharacterEngine
from app.engines.interaction_engine import InteractionEngine
from app.engines.media_pipeline import MediaPipeline
from app.engines.scene_engine import SceneEngine
from app.engines.simulation_engine import SimulationEngine
from app.pipelines.generation_pipeline import GenerationPipeline
from app.repositories.snapshot_repository import SnapshotRepository
from app.repositories.universe_repository import UniverseRepository
from app.repositories.world_state_repository import WorldStateRepository
from app.services.gemini_client import GeminiClient
from app.services.image_service import ImageService
from app.services.pipeline_service import PipelineService
from app.services.storage_service import StorageService
from app.services.story_service import StoryService
from app.storage.backblaze import BackblazeClient
from app.storage.storage_manager import StorageManager


class GeminiClientAdapter:
    """Adapts GeminiClient to the AIClient interface used by engines."""

    def __init__(self, gemini_client: GeminiClient) -> None:
        self.gemini_client = gemini_client

    def generate(self, prompt: str) -> str:
        return self.gemini_client.generate_text(prompt)


@lru_cache
def _get_gemini_client(api_key: str) -> GeminiClient:
    return GeminiClient(api_key=api_key)


@lru_cache
def _get_backblaze_client(
    key_id: str, application_key: str, bucket: str, endpoint: str
) -> BackblazeClient:
    return BackblazeClient(
        key_id=key_id,
        application_key=application_key,
        bucket=bucket,
        endpoint=endpoint,
    )


@lru_cache
def _get_image_service() -> ImageService:
    return ImageService()


def get_storage_base_dir() -> Path:
    storage_dir = os.getenv("HEADCANON_STORAGE_DIR", "data")
    p = Path(storage_dir)
    p.mkdir(parents=True, exist_ok=True)
    return p


def get_universe_repository(
    base_dir: Path = Depends(get_storage_base_dir),
) -> UniverseRepository:
    return UniverseRepository(base_dir=base_dir)


def get_world_state_repository(
    base_dir: Path = Depends(get_storage_base_dir),
) -> WorldStateRepository:
    return WorldStateRepository(base_dir=base_dir)


def get_snapshot_repository(
    base_dir: Path = Depends(get_storage_base_dir),
) -> SnapshotRepository:
    return SnapshotRepository(base_dir=base_dir)


def get_storage_manager(
    base_dir: Path = Depends(get_storage_base_dir),
) -> StorageManager:
    return StorageManager(base_dir=base_dir)


def get_ai_adapter(settings: Settings = Depends(get_settings)) -> GeminiClientAdapter | None:
    if not settings.google_api_key:
        return None
    gemini = _get_gemini_client(api_key=settings.google_api_key)
    return GeminiClientAdapter(gemini)


def get_character_engine(
    ai_adapter: GeminiClientAdapter | None = Depends(get_ai_adapter),
) -> CharacterEngine:
    return CharacterEngine(ai_client=ai_adapter)


def get_scene_engine(
    ai_adapter: GeminiClientAdapter | None = Depends(get_ai_adapter),
) -> SceneEngine:
    return SceneEngine(ai_client=ai_adapter)


def get_interaction_engine(
    ai_adapter: GeminiClientAdapter | None = Depends(get_ai_adapter),
    character_engine: CharacterEngine = Depends(get_character_engine),
    scene_engine: SceneEngine = Depends(get_scene_engine),
) -> InteractionEngine:
    return InteractionEngine(
        ai_client=ai_adapter,
        character_engine=character_engine,
        scene_engine=scene_engine,
    )


def get_simulation_engine(
    ai_adapter: GeminiClientAdapter | None = Depends(get_ai_adapter),
) -> SimulationEngine:
    return SimulationEngine(ai_client=ai_adapter)


def get_media_pipeline(
    ai_adapter: GeminiClientAdapter | None = Depends(get_ai_adapter),
) -> MediaPipeline:
    return MediaPipeline(ai_client=ai_adapter)


# ---------------------------------------------------------------------------
# Legacy Services Dependencies (Retained for backwards compatibility)
# ---------------------------------------------------------------------------


def get_backblaze_client(settings: Settings = Depends(get_settings)) -> BackblazeClient:
    return _get_backblaze_client(
        key_id=settings.backblaze_key_id,
        application_key=settings.backblaze_application_key,
        bucket=settings.backblaze_bucket,
        endpoint=settings.backblaze_endpoint,
    )


def get_storage_service(
    client: BackblazeClient = Depends(get_backblaze_client),
) -> StorageService:
    return StorageService(client=client)


def get_story_service(
    storage_service: StorageService = Depends(get_storage_service),
    settings: Settings = Depends(get_settings),
) -> StoryService:
    client = _get_gemini_client(api_key=settings.google_api_key)
    return StoryService(gemini=client, storage=storage_service)


def get_image_service() -> ImageService:
    return _get_image_service()


def get_generation_pipeline(
    story_service: StoryService = Depends(get_story_service),
    image_service: ImageService = Depends(get_image_service),
    storage_service: StorageService = Depends(get_storage_service),
) -> GenerationPipeline:
    return GenerationPipeline(
        story_service=story_service,
        image_service=image_service,
        storage_service=storage_service,
    )


def get_pipeline_service(
    pipeline: GenerationPipeline = Depends(get_generation_pipeline),
) -> PipelineService:
    return PipelineService(pipeline=pipeline)
