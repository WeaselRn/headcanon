"""
Tests for POST /api/stories (story generation) and the remaining 501 scaffolded routes.

POST /api/stories is tested using FastAPI dependency_overrides so no real Gemini call is made.
"""

from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import get_story_service
from app.main import app
from app.models.metadata import StoryMetadata
from app.models.scene import Scene
from app.models.story import Story

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
            image_url="",
        ),
        Scene(
            scene_number=2,
            title="The Hidden Door",
            description="A door appears behind a tapestry.",
            image_prompt="An ancient wooden door hidden behind a tattered tapestry.",
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

_VALID_REQUEST = {
    "universe": "Harry Potter",
    "character_name": "Elias",
    "role": "Student",
    "mood": "Dark",
    "prompt": "The castle hides an ancient secret.",
}


def _make_client(mock_service: MagicMock) -> TestClient:
    """Return a TestClient with get_story_service overridden."""
    app.dependency_overrides[get_story_service] = lambda: mock_service
    c = TestClient(app)
    return c


def _clear_overrides() -> None:
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# POST /api/stories
# ---------------------------------------------------------------------------


def test_create_story_returns_201() -> None:
    """POST /api/stories returns 201 and a well-formed Story when the service succeeds."""
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


def test_create_story_calls_service_generate() -> None:
    """The route delegates to StoryService.generate with the correct request."""
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
    """If the service raises ValueError (bad JSON from Gemini), return 422."""
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
# Remaining scaffolded routes still return 501
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "method,url,body",
    [
        ("GET", "/api/stories", None),
        ("GET", "/api/stories/some-uuid", None),
        ("POST", "/api/stories/some-uuid/continue", {"prompt": "Continue."}),
        ("POST", "/api/stories/some-uuid/regenerate-scene", {"scene_number": 2}),
        ("DELETE", "/api/stories/some-uuid", None),
    ],
)
def test_unimplemented_routes_return_501(method: str, url: str, body: dict | None) -> None:
    response = TestClient(app).request(method, url, json=body)
    assert response.status_code == 501
