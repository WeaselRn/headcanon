from functools import lru_cache

from fastapi import Depends

from app.config.settings import Settings, get_settings
from app.services.gemini_client import GeminiClient
from app.services.story_service import StoryService


@lru_cache
def _get_gemini_client(api_key: str) -> GeminiClient:
    return GeminiClient(api_key=api_key)


def get_story_service(settings: Settings = Depends(get_settings)) -> StoryService:
    client = _get_gemini_client(api_key=settings.google_api_key)
    return StoryService(gemini=client)
