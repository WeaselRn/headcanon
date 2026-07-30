import logging

from app.models.story import Story
from app.pipelines.generation_pipeline import GenerationPipeline
from app.schemas.generation import GenerationRequest

logger = logging.getLogger(__name__)


class PipelineService:
    def __init__(self, pipeline: GenerationPipeline) -> None:
        self.pipeline = pipeline

    def run(self, request: GenerationRequest) -> Story:
        logger.info("Executing pipeline service")
        return self.pipeline.run(request)
