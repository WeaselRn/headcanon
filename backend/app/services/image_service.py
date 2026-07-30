import logging
from io import BytesIO

from PIL import Image, ImageDraw

logger = logging.getLogger(__name__)


class ImageService:
    def generate_image(self, prompt: str) -> bytes:
        logger.info("Generating image for prompt: %r", prompt[:60])
        width, height = 800, 600
        image = Image.new("RGB", (width, height), color=(24, 24, 38))
        draw = ImageDraw.Draw(image)

        draw.rectangle([20, 20, width - 20, height - 20], outline=(120, 90, 200), width=3)

        label = prompt if len(prompt) <= 60 else prompt[:57] + "..."
        draw.text((width // 2, height // 2), label, fill=(230, 230, 250), anchor="mm")

        buffer = BytesIO()
        image.save(buffer, format="PNG")
        return buffer.getvalue()

    def regenerate_scene(self, story_id: str, scene_number: int) -> str:
        raise NotImplementedError
