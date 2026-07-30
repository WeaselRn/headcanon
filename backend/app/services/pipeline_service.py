import logging

from app.models.story import Story
from app.schemas.generation import GenerationRequest

logger = logging.getLogger(__name__)


class PipelineService:
    def run(self, request: GenerationRequest) -> Story:
        raise NotImplementedError
