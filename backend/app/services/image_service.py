import logging

logger = logging.getLogger(__name__)


class ImageService:
    def generate_image(self, prompt: str) -> str:
        raise NotImplementedError

    def regenerate_scene(self, story_id: str, scene_number: int) -> str:
        raise NotImplementedError
