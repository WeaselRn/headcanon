import logging

from app.models.story import Story, StoryCard
from app.schemas.generation import ContinueStoryRequest, GenerationRequest

logger = logging.getLogger(__name__)


class StoryService:
    def generate(self, request: GenerationRequest) -> Story:
        raise NotImplementedError

    def list_stories(self) -> list[StoryCard]:
        raise NotImplementedError

    def get_story(self, story_id: str) -> Story:
        raise NotImplementedError

    def continue_story(self, story_id: str, request: ContinueStoryRequest) -> Story:
        raise NotImplementedError

    def delete_story(self, story_id: str) -> None:
        raise NotImplementedError
