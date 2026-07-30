"""
Tests for /api/stories endpoints (POST, GET, GET {id}, DELETE {id}) and remaining 501 routes.
"""

from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import get_pipeline_service, get_story_service
from app.main import app
from app.models.metadata import StoryMetadata
from app.models.scene import Scene
from app.models.story import Story, StoryCard

# ---------------------------------------------------------------------------
# Shared fixture data
# ---------------------------------------------------------------------------

_NOW = datetime.now(tz=UTC)

_FAKE_STORY = Story(
    story_id="test-uuid-001",
    title="The Hidden Chamber",
    universe="Harry Potter",
    character_name="Elias",
    role="Student",
    mood="Dark",
    story="Once upon a time in a castle filled with secrets...",
    scenes=[
        Scene(
            scene_number=1,
            title="The Dark Corridor",
            description="Elias walks through a torchlit hallway.",
            image_prompt="A dark stone corridor lit by flickering torches.",
            image_url="https://example.com/scene_01.png",
        ),
        Scene(
            scene_number=2,
            title="The Hidden Door",
            description="A door appears behind a tapestry.",
            image_prompt="An ancient wooden door hidden behind a tattered tapestry.",
            image_url="https://example.com/scene_02.png",
        ),
    ],
    metadata=StoryMetadata(
        created_at=_NOW,
        updated_at=_NOW,
        models=["gemini-2.0-flash"],
        pipeline_version="v1",
    ),
)

_VALID_REQUEST = {
    "universe": "Harry Potter",
    "character_name": "Elias",
    "role": "Student",
    "mood": "Dark",
    "prompt": "The castle hides an ancient secret.",
}


def _make_client(mock_service: MagicMock) -> TestClient:
    """Return a TestClient with dependencies overridden."""
    mock_pipeline_service = MagicMock()
    mock_pipeline_service.run.side_effect = mock_service.generate
    app.dependency_overrides[get_story_service] = lambda: mock_service
    app.dependency_overrides[get_pipeline_service] = lambda: mock_pipeline_service
    c = TestClient(app)
    return c


def _clear_overrides() -> None:
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# POST /api/stories
# ---------------------------------------------------------------------------


def test_create_story_returns_201() -> None:
    """POST /api/stories returns 201 and a well-formed Story when the pipeline succeeds."""
    mock_service = MagicMock()
    mock_service.generate.return_value = _FAKE_STORY
    c = _make_client(mock_service)
    try:
        response = c.post("/api/stories", json=_VALID_REQUEST)
    finally:
        _clear_overrides()

    assert response.status_code == 201
    data = response.json()
    assert data["story_id"] == "test-uuid-001"
    assert data["title"] == "The Hidden Chamber"
    assert data["universe"] == "Harry Potter"
    assert len(data["scenes"]) == 2
    assert data["scenes"][0]["scene_number"] == 1


def test_create_story_calls_pipeline_run() -> None:
    """The route delegates to PipelineService.run with the correct request."""
    mock_service = MagicMock()
    mock_service.generate.return_value = _FAKE_STORY
    c = _make_client(mock_service)
    try:
        c.post("/api/stories", json=_VALID_REQUEST)
    finally:
        _clear_overrides()

    mock_service.generate.assert_called_once()
    call_arg = mock_service.generate.call_args[0][0]
    assert call_arg.universe == "Harry Potter"
    assert call_arg.character_name == "Elias"


def test_create_story_validation_error_returns_422() -> None:
    """Missing required fields yield 422 (FastAPI validation, no service call needed)."""
    response = TestClient(app).post("/api/stories", json={"universe": "Harry Potter"})
    assert response.status_code == 422


def test_create_story_service_value_error_returns_422() -> None:
    """If the pipeline raises ValueError (bad JSON from Gemini), return 422."""
    mock_service = MagicMock()
    mock_service.generate.side_effect = ValueError("Gemini returned invalid JSON")
    c = _make_client(mock_service)
    try:
        response = c.post("/api/stories", json=_VALID_REQUEST)
    finally:
        _clear_overrides()

    assert response.status_code == 422


def test_create_story_service_runtime_error_returns_500() -> None:
    """Unexpected exceptions from the service return 500."""
    mock_service = MagicMock()
    mock_service.generate.side_effect = RuntimeError("network timeout")
    c = _make_client(mock_service)
    try:
        response = c.post("/api/stories", json=_VALID_REQUEST)
    finally:
        _clear_overrides()

    assert response.status_code == 500


# ---------------------------------------------------------------------------
# GET /api/stories
# ---------------------------------------------------------------------------


def test_list_stories_returns_200() -> None:
    mock_service = MagicMock()
    mock_service.list_stories.return_value = [
        StoryCard(story_id="test-uuid-001", title="The Hidden Chamber", thumbnail="")
    ]
    c = _make_client(mock_service)
    try:
        response = c.get("/api/stories")
    finally:
        _clear_overrides()

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["story_id"] == "test-uuid-001"
    assert data[0]["title"] == "The Hidden Chamber"


# ---------------------------------------------------------------------------
# GET /api/stories/{story_id}
# ---------------------------------------------------------------------------


def test_get_story_returns_200() -> None:
    mock_service = MagicMock()
    mock_service.get_story.return_value = _FAKE_STORY
    c = _make_client(mock_service)
    try:
        response = c.get("/api/stories/test-uuid-001")
    finally:
        _clear_overrides()

    assert response.status_code == 200
    data = response.json()
    assert data["story_id"] == "test-uuid-001"
    assert data["title"] == "The Hidden Chamber"


def test_get_story_not_found_returns_404() -> None:
    mock_service = MagicMock()
    mock_service.get_story.side_effect = FileNotFoundError("Story not found")
    c = _make_client(mock_service)
    try:
        response = c.get("/api/stories/non-existent")
    finally:
        _clear_overrides()

    assert response.status_code == 404
    assert response.json() == {"error": "Story not found"}


# ---------------------------------------------------------------------------
# DELETE /api/stories/{story_id}
# ---------------------------------------------------------------------------


def test_delete_story_returns_204() -> None:
    mock_service = MagicMock()
    mock_service.delete_story.return_value = None
    c = _make_client(mock_service)
    try:
        response = c.delete("/api/stories/test-uuid-001")
    finally:
        _clear_overrides()

    assert response.status_code == 204
    mock_service.delete_story.assert_called_once_with("test-uuid-001")


def test_delete_story_not_found_returns_404() -> None:
    mock_service = MagicMock()
    mock_service.delete_story.side_effect = FileNotFoundError("Story not found")
    c = _make_client(mock_service)
    try:
        response = c.delete("/api/stories/non-existent")
    finally:
        _clear_overrides()

    assert response.status_code == 404
    assert response.json() == {"error": "Story not found"}


# ---------------------------------------------------------------------------
# Remaining scaffolded routes still return 501
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "method,url,body",
    [
        ("POST", "/api/stories/some-uuid/continue", {"prompt": "Continue."}),
        ("POST", "/api/stories/some-uuid/regenerate-scene", {"scene_number": 2}),
    ],
)
def test_unimplemented_routes_return_501(method: str, url: str, body: dict | None) -> None:
    response = TestClient(app).request(method, url, json=body)
    assert response.status_code == 501
