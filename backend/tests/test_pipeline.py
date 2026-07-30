from datetime import UTC, datetime
from unittest.mock import MagicMock

from app.models.metadata import StoryMetadata
from app.models.scene import Scene
from app.models.story import Story
from app.pipelines.generation_pipeline import GenerationPipeline
from app.schemas.generation import GenerationRequest
from app.services.pipeline_service import PipelineService

_NOW = datetime.now(tz=UTC)

_RAW_STORY = Story(
    story_id="pipe-uuid-101",
    title="The Silver Dragon",
    universe="Fantasy",
    character_name="Lyra",
    role="Mage",
    mood="Epic",
    story="Lyra stood atop the stormy peak facing the silver dragon.",
    scenes=[
        Scene(
            scene_number=1,
            title="Stormy Peak",
            description="Lyra reaches the top of the mountain.",
            image_prompt="A mage standing on a stormy mountain peak.",
            image_url="",
        ),
        Scene(
            scene_number=2,
            title="The Dragon Awakes",
            description="A silver dragon emerges from the clouds.",
            image_prompt="A majestic silver dragon emerging from dark clouds.",
            image_url="",
        ),
    ],
    metadata=StoryMetadata(
        created_at=_NOW,
        updated_at=_NOW,
        models=["gemini-2.0-flash"],
        pipeline_version="v1",
    ),
)

_REQUEST = GenerationRequest(
    universe="Fantasy",
    character_name="Lyra",
    role="Mage",
    mood="Epic",
    prompt="Facing the silver dragon.",
)


def test_generation_pipeline_runs_full_orchestration() -> None:
    mock_story_service = MagicMock()
    mock_story_service.generate_raw.return_value = _RAW_STORY

    mock_image_service = MagicMock()
    mock_image_service.generate_image.return_value = b"fake-png-bytes"

    mock_storage_service = MagicMock()
    mock_storage_service.upload.side_effect = lambda key, data, content_type: (
        f"https://headcanon.b2/{key}"
    )

    pipeline = GenerationPipeline(
        story_service=mock_story_service,
        image_service=mock_image_service,
        storage_service=mock_storage_service,
    )

    story = pipeline.run(_REQUEST)

    # 1. Story text generated via generate_raw
    mock_story_service.generate_raw.assert_called_once_with(_REQUEST)

    # 2. Images generated for 2 scenes + 1 thumbnail = 3 calls
    assert mock_image_service.generate_image.call_count == 3

    # 3. Images uploaded to B2 storage
    assert mock_storage_service.upload.call_count == 3
    uploaded_keys = [call[0][0] for call in mock_storage_service.upload.call_args_list]
    assert "stories/pipe-uuid-101/scenes/scene_01.png" in uploaded_keys
    assert "stories/pipe-uuid-101/scenes/scene_02.png" in uploaded_keys
    assert "stories/pipe-uuid-101/thumbnail.png" in uploaded_keys

    # 4. Scene image_urls updated in story
    assert (
        story.scenes[0].image_url
        == "https://headcanon.b2/stories/pipe-uuid-101/scenes/scene_01.png"
    )
    assert (
        story.scenes[1].image_url
        == "https://headcanon.b2/stories/pipe-uuid-101/scenes/scene_02.png"
    )

    # 5. Manifest & story saved to storage
    mock_storage_service.save_story.assert_called_once()
    saved_story, provenance = mock_storage_service.save_story.call_args[0]
    assert saved_story.story_id == "pipe-uuid-101"
    assert provenance.execution_id == "pipe-uuid-101"
    assert "image-gen-v1" in provenance.models_used
    assert "thumbnail.png" in provenance.assets_generated


def test_pipeline_service_delegates_to_pipeline() -> None:
    mock_pipeline = MagicMock()
    mock_pipeline.run.return_value = _RAW_STORY

    service = PipelineService(pipeline=mock_pipeline)
    result = service.run(_REQUEST)

    mock_pipeline.run.assert_called_once_with(_REQUEST)
    assert result == _RAW_STORY
