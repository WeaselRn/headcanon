import logging

from app.models.story import Story
from app.schemas.generation import GenerationRequest

logger = logging.getLogger(__name__)


class GenerationPipeline:
    """
    Orchestrates the full story-generation pipeline:
    Generate Story → Split Scenes → Generate Images →
    Generate Narration → Generate Music → Upload Assets →
    Generate Manifest → Return Story
    """

    def run(self, request: GenerationRequest) -> Story:
        raise NotImplementedError
