import logging
from datetime import UTC, datetime

from app.models.provenance import Provenance
from app.models.story import Story
from app.schemas.generation import ContinueStoryRequest, GenerationRequest
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
        storage_locations: list[str] = [
            f"stories/{story.story_id}/story.md",
            f"stories/{story.story_id}/metadata.json",
            f"stories/{story.story_id}/provenance.json",
        ]

        # 3. Generate Images for Scenes & Upload to Storage
        for scene in story.scenes:
            logger.info("Generating image for scene %d", scene.scene_number)
            img_bytes = self.image_service.generate_image(scene.image_prompt)
            scene_key = f"stories/{story.story_id}/scenes/scene_{scene.scene_number:02d}.png"
            img_url = self.storage_service.upload(scene_key, img_bytes, content_type="image/png")
            scene.image_url = img_url
            assets_generated.append(f"scenes/scene_{scene.scene_number:02d}.png")
            storage_locations.append(scene_key)

        # 4. Generate Story Thumbnail & Upload
        thumb_bytes = self.image_service.generate_image(f"Thumbnail for {story.title}")
        thumb_key = f"stories/{story.story_id}/thumbnail.png"
        self.storage_service.upload(thumb_key, thumb_bytes, content_type="image/png")
        assets_generated.append("thumbnail.png")
        storage_locations.append(thumb_key)

        # 5. Metadata & Provenance
        completed_at = datetime.now(tz=UTC)
        provenance = Provenance(
            execution_id=story.story_id,
            pipeline_version=story.metadata.pipeline_version,
            models_used=story.metadata.models + ["image-gen-v1"],
            started_at=started_at,
            completed_at=completed_at,
            assets_generated=assets_generated,
            status="completed",
            storage_locations=storage_locations,
        )
        story.provenance = provenance

        # 6. Upload Manifest/Story & Assets
        self.storage_service.save_story(story, provenance)

        logger.info("Pipeline completed successfully for story %s", story.story_id)
        return story

    def continue_story(self, story_id: str, request: ContinueStoryRequest) -> Story:
        started_at = datetime.now(tz=UTC)
        logger.info("Starting continuation pipeline for story %s", story_id)

        # 1. Load existing story from storage
        existing_story = self.storage_service.get_story(story_id)

        # 2. Generate continuation text and new scenes
        continuation_text, new_scenes = self.story_service.generate_continuation_raw(
            existing_story, request
        )
        existing_story.story = f"{existing_story.story}\n\n{continuation_text}"

        # 3. Generate images for new scenes and upload to B2 storage
        for scene in new_scenes:
            logger.info("Generating image for continuation scene %d", scene.scene_number)
            img_bytes = self.image_service.generate_image(scene.image_prompt)
            scene_key = f"stories/{story_id}/scenes/scene_{scene.scene_number:02d}.png"
            img_url = self.storage_service.upload(scene_key, img_bytes, content_type="image/png")
            scene.image_url = img_url
            existing_story.scenes.append(scene)

        # 4. Update metadata timestamp
        completed_at = datetime.now(tz=UTC)
        existing_story.metadata.updated_at = completed_at

        # 5. Build updated asset list and Provenance
        assets_generated: list[str] = [
            "story.md",
            "metadata.json",
            "provenance.json",
            "thumbnail.png",
        ]
        storage_locations: list[str] = [
            f"stories/{story_id}/story.md",
            f"stories/{story_id}/metadata.json",
            f"stories/{story_id}/provenance.json",
            f"stories/{story_id}/thumbnail.png",
        ]
        for scene in existing_story.scenes:
            assets_generated.append(f"scenes/scene_{scene.scene_number:02d}.png")
            storage_locations.append(
                f"stories/{story_id}/scenes/scene_{scene.scene_number:02d}.png"
            )

        provenance = Provenance(
            execution_id=story_id,
            pipeline_version=existing_story.metadata.pipeline_version,
            models_used=existing_story.metadata.models + ["image-gen-v1"],
            started_at=started_at,
            completed_at=completed_at,
            assets_generated=assets_generated,
            status="completed",
            storage_locations=storage_locations,
        )
        existing_story.provenance = provenance

        # 6. Upload updated story files to storage
        self.storage_service.save_story(existing_story, provenance)

        logger.info("Continuation pipeline completed successfully for story %s", story_id)
        return existing_story
