from functools import lru_cache

from fastapi import Depends

from app.config.settings import Settings, get_settings
from app.pipelines.generation_pipeline import GenerationPipeline
from app.services.gemini_client import GeminiClient
from app.services.image_service import ImageService
from app.services.pipeline_service import PipelineService
from app.services.storage_service import StorageService
from app.services.story_service import StoryService
from app.storage.backblaze import BackblazeClient


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
