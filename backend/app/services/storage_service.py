import json
import logging
from datetime import UTC, datetime
from typing import Any

from app.models.provenance import Provenance
from app.models.story import Story, StoryCard
from app.storage.backblaze import BackblazeClient

logger = logging.getLogger(__name__)


class StorageService:
    def __init__(self, client: BackblazeClient) -> None:
        self.client = client

    def save_story(self, story: Story, provenance: Provenance | None = None) -> Story:
        prefix = f"stories/{story.story_id}/"
        logger.info("Saving story %s to storage", story.story_id)

        if provenance is None:
            now = datetime.now(tz=UTC)
            provenance = Provenance(
                execution_id=story.story_id,
                pipeline_version=story.metadata.pipeline_version,
                models_used=story.metadata.models,
                started_at=now,
                completed_at=now,
                assets_generated=["story.md", "metadata.json", "provenance.json"],
                status="completed",
                storage_locations=[
                    f"{prefix}story.md",
                    f"{prefix}metadata.json",
                    f"{prefix}provenance.json",
                ],
            )

        story.provenance = provenance

        # 1. story.md
        story_md_key = f"{prefix}story.md"
        self.client.upload(story_md_key, story.story.encode("utf-8"), content_type="text/markdown")

        # 2. metadata.json
        metadata_key = f"{prefix}metadata.json"
        self.client.upload(
            metadata_key,
            story.model_dump_json().encode("utf-8"),
            content_type="application/json",
        )

        # 3. provenance.json
        provenance_key = f"{prefix}provenance.json"
        self.client.upload(
            provenance_key,
            provenance.model_dump_json().encode("utf-8"),
            content_type="application/json",
        )

        return story

    def get_story(self, story_id: str) -> Story:
        metadata_key = f"stories/{story_id}/metadata.json"
        provenance_key = f"stories/{story_id}/provenance.json"
        logger.info("Getting story %s from storage", story_id)
        try:
            data = self.client.download(metadata_key)
            story_dict: dict[str, Any] = json.loads(data.decode("utf-8"))
            story = Story.model_validate(story_dict)

            if story.provenance is None:
                try:
                    prov_data = self.client.download(provenance_key)
                    prov_dict: dict[str, Any] = json.loads(prov_data.decode("utf-8"))
                    story.provenance = Provenance.model_validate(prov_dict)
                except FileNotFoundError:
                    logger.warning("Provenance file not found for story %s", story_id)
                except Exception as exc:
                    logger.warning("Failed to parse provenance for story %s: %s", story_id, exc)

            return story
        except FileNotFoundError as exc:
            raise FileNotFoundError(f"Story '{story_id}' not found.") from exc

    def list_stories(self) -> list[StoryCard]:
        logger.info("Listing all stories from storage")
        all_keys = self.client.list_keys("stories/")
        metadata_keys = [k for k in all_keys if k.endswith("/metadata.json")]

        cards: list[StoryCard] = []
        for meta_key in metadata_keys:
            try:
                data = self.client.download(meta_key)
                story_dict: dict[str, Any] = json.loads(data.decode("utf-8"))
                story_id = str(story_dict.get("story_id", ""))
                title = str(story_dict.get("title", ""))
                thumbnail = str(story_dict.get("thumbnail", ""))
                if not thumbnail and "scenes" in story_dict and len(story_dict["scenes"]) > 0:
                    first_scene = story_dict["scenes"][0]
                    if isinstance(first_scene, dict):
                        thumbnail = str(first_scene.get("image_url", ""))
                cards.append(StoryCard(story_id=story_id, title=title, thumbnail=thumbnail))
            except Exception as exc:
                logger.warning("Failed to parse metadata key %s: %s", meta_key, exc)

        return cards

    def delete_story(self, story_id: str) -> None:
        prefix = f"stories/{story_id}/"
        logger.info("Deleting story %s from storage", story_id)
        existing_keys = self.client.list_keys(prefix)
        if not existing_keys:
            raise FileNotFoundError(f"Story '{story_id}' not found.")
        self.client.delete_prefix(prefix)

    def upload(self, key: str, data: bytes, content_type: str = "application/octet-stream") -> str:
        return self.client.upload(key, data, content_type)

    def download(self, key: str) -> bytes:
        return self.client.download(key)

    def delete(self, key: str) -> None:
        self.client.delete(key)

    def list_keys(self, prefix: str = "") -> list[str]:
        return self.client.list_keys(prefix)
