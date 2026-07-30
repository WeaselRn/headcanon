from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest

from app.models.metadata import StoryMetadata
from app.models.scene import Scene
from app.models.story import Story
from app.services.storage_service import StorageService

_NOW = datetime.now(tz=UTC)

_SAMPLE_STORY = Story(
    story_id="story-uuid-999",
    title="The Golden Quill",
    universe="Original",
    character_name="Arthur",
    role="Writer",
    mood="Inspiring",
    story="Once upon a time Arthur found a quill.",
    scenes=[
        Scene(
            scene_number=1,
            title="Finding the Quill",
            description="Arthur spots a glowing quill.",
            image_prompt="A glowing golden quill on an oak desk.",
            image_url="https://example.com/scene_01.png",
        )
    ],
    metadata=StoryMetadata(
        created_at=_NOW,
        updated_at=_NOW,
        models=["gemini-2.0-flash"],
        pipeline_version="v1",
    ),
)


def test_save_story() -> None:
    mock_client = MagicMock()
    service = StorageService(client=mock_client)

    saved_story = service.save_story(_SAMPLE_STORY)
    assert saved_story.story_id == "story-uuid-999"

    # Expect 3 uploads: story.md, metadata.json, provenance.json
    assert mock_client.upload.call_count == 3
    uploaded_keys = [call[0][0] for call in mock_client.upload.call_args_list]
    assert "stories/story-uuid-999/story.md" in uploaded_keys
    assert "stories/story-uuid-999/metadata.json" in uploaded_keys
    assert "stories/story-uuid-999/provenance.json" in uploaded_keys


def test_get_story_success() -> None:
    mock_client = MagicMock()
    mock_client.download.return_value = _SAMPLE_STORY.model_dump_json().encode("utf-8")
    service = StorageService(client=mock_client)

    story = service.get_story("story-uuid-999")
    assert story.story_id == "story-uuid-999"
    assert story.title == "The Golden Quill"
    mock_client.download.assert_called_once_with("stories/story-uuid-999/metadata.json")


def test_get_story_not_found() -> None:
    mock_client = MagicMock()
    mock_client.download.side_effect = FileNotFoundError("Key not found")
    service = StorageService(client=mock_client)

    with pytest.raises(FileNotFoundError, match="not found"):
        service.get_story("non-existent-uuid")


def test_list_stories() -> None:
    mock_client = MagicMock()
    mock_client.list_keys.return_value = [
        "stories/story-uuid-999/metadata.json",
        "stories/story-uuid-999/story.md",
    ]
    mock_client.download.return_value = _SAMPLE_STORY.model_dump_json().encode("utf-8")
    service = StorageService(client=mock_client)

    cards = service.list_stories()
    assert len(cards) == 1
    assert cards[0].story_id == "story-uuid-999"
    assert cards[0].title == "The Golden Quill"
    assert cards[0].thumbnail == "https://example.com/scene_01.png"


def test_delete_story_success() -> None:
    mock_client = MagicMock()
    mock_client.list_keys.return_value = [
        "stories/story-uuid-999/metadata.json",
        "stories/story-uuid-999/story.md",
    ]
    service = StorageService(client=mock_client)

    service.delete_story("story-uuid-999")
    mock_client.delete_prefix.assert_called_once_with("stories/story-uuid-999/")


def test_delete_story_not_found() -> None:
    mock_client = MagicMock()
    mock_client.list_keys.return_value = []
    service = StorageService(client=mock_client)

    with pytest.raises(FileNotFoundError, match="not found"):
        service.delete_story("non-existent-uuid")
