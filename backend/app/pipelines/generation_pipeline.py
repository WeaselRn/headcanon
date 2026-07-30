import logging
from datetime import UTC, datetime

from app.models.provenance import Provenance
from app.models.story import Story
from app.schemas.generation import GenerationRequest
from app.services.image_service import ImageService
from app.services.storage_service import StorageService
from app.services.story_service import StoryService

logger = logging.getLogger(__name__)


class GenerationPipeline:
    """
    Orchestrates the full story-generation pipeline:
    User Prompt → Generate Story → Split Scenes → Image Prompt Generation →
    Generate Images → Upload Assets → Metadata & Provenance → Return Story
    """

    def __init__(
        self,
        story_service: StoryService,
        image_service: ImageService,
        storage_service: StorageService,
    ) -> None:
        self.story_service = story_service
        self.image_service = image_service
        self.storage_service = storage_service

    def run(self, request: GenerationRequest) -> Story:
        started_at = datetime.now(tz=UTC)
        logger.info("Starting generation pipeline for universe %r", request.universe)

        # 1 & 2. Generate Story & Split Scenes (with image prompts)
        story = self.story_service.generate_raw(request)
        assets_generated: list[str] = ["story.md", "metadata.json", "provenance.json"]

        # 3. Generate Images for Scenes & Upload to Storage
        for scene in story.scenes:
            logger.info("Generating image for scene %d", scene.scene_number)
            img_bytes = self.image_service.generate_image(scene.image_prompt)
            scene_key = f"stories/{story.story_id}/scenes/scene_{scene.scene_number:02d}.png"
            img_url = self.storage_service.upload(scene_key, img_bytes, content_type="image/png")
            scene.image_url = img_url
            assets_generated.append(f"scenes/scene_{scene.scene_number:02d}.png")

        # 4. Generate Story Thumbnail & Upload
        thumb_bytes = self.image_service.generate_image(f"Thumbnail for {story.title}")
        thumb_key = f"stories/{story.story_id}/thumbnail.png"
        self.storage_service.upload(thumb_key, thumb_bytes, content_type="image/png")
        assets_generated.append("thumbnail.png")

        # 5. Metadata & Provenance
        completed_at = datetime.now(tz=UTC)
        provenance = Provenance(
            execution_id=story.story_id,
            pipeline_version=story.metadata.pipeline_version,
            models_used=story.metadata.models + ["image-gen-v1"],
            started_at=started_at,
            completed_at=completed_at,
            assets_generated=assets_generated,
        )

        # 6. Upload Manifest/Story & Assets
        self.storage_service.save_story(story, provenance)

        logger.info("Pipeline completed successfully for story %s", story.story_id)
        return story
