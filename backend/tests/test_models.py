from datetime import UTC, datetime

from app.models.metadata import StoryMetadata
from app.models.provenance import Provenance
from app.models.scene import Scene
from app.models.story import Story, StoryCard


def _make_metadata() -> StoryMetadata:
    now = datetime.now(tz=UTC)
    return StoryMetadata(
        created_at=now,
        updated_at=now,
        models=["gemini-pro"],
        pipeline_version="v1",
    )


def _make_scene() -> Scene:
    return Scene(
        scene_number=1,
        title="The Dark Hall",
        description="A long corridor lit by torches.",
        image_prompt="dark hallway torches stone",
        image_url="https://example.com/scene_01.png",
    )


def test_scene_model() -> None:
    scene = _make_scene()
    assert scene.scene_number == 1
    assert scene.image_url == "https://example.com/scene_01.png"


def test_story_metadata_model() -> None:
    meta = _make_metadata()
    assert meta.pipeline_version == "v1"
    assert "gemini-pro" in meta.models


def test_provenance_model() -> None:
    now = datetime.now(tz=UTC)
    prov = Provenance(
        execution_id="exec-123",
        pipeline_version="v1",
        models_used=["gemini-pro"],
        started_at=now,
        completed_at=now,
        assets_generated=["scene_01.png"],
        status="completed",
        storage_locations=["stories/exec-123/scene_01.png"],
    )
    assert prov.execution_id == "exec-123"
    assert prov.assets_generated == ["scene_01.png"]
    assert prov.status == "completed"
    assert prov.storage_locations == ["stories/exec-123/scene_01.png"]


def test_story_model() -> None:
    now = datetime.now(tz=UTC)
    prov = Provenance(
        execution_id="uuid-001",
        pipeline_version="v1",
        models_used=["gemini-pro"],
        started_at=now,
        completed_at=now,
        assets_generated=["story.md"],
    )
    story = Story(
        story_id="uuid-001",
        title="The Hidden Chamber",
        universe="Harry Potter",
        character_name="Elias",
        role="Student",
        mood="Dark",
        story="Once upon a time...",
        scenes=[_make_scene()],
        metadata=_make_metadata(),
        provenance=prov,
    )
    assert story.story_id == "uuid-001"
    assert len(story.scenes) == 1
    assert story.provenance is not None
    assert story.provenance.execution_id == "uuid-001"


def test_story_card_model() -> None:
    card = StoryCard(
        story_id="uuid-001",
        title="The Hidden Chamber",
        thumbnail="https://example.com/thumb.png",
    )
    assert card.thumbnail == "https://example.com/thumb.png"
