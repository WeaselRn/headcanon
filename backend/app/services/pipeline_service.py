import logging

from app.models.story import Story
from app.pipelines.generation_pipeline import GenerationPipeline
from app.schemas.generation import ContinueStoryRequest, GenerationRequest

logger = logging.getLogger(__name__)


class PipelineService:
    def __init__(self, pipeline: GenerationPipeline) -> None:
        self.pipeline = pipeline

    def run(self, request: GenerationRequest) -> Story:
        logger.info("Executing pipeline service run")
        return self.pipeline.run(request)

    def continue_story(self, story_id: str, request: ContinueStoryRequest) -> Story:
        logger.info("Executing pipeline service continue_story for id=%s", story_id)
        return self.pipeline.continue_story(story_id, request)
