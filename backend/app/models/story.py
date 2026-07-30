from pydantic import BaseModel

from app.models.metadata import StoryMetadata
from app.models.provenance import Provenance
from app.models.scene import Scene


class Story(BaseModel):
    story_id: str
    title: str
    universe: str
    character_name: str
    role: str
    mood: str
    story: str
    scenes: list[Scene]
    metadata: StoryMetadata
    provenance: Provenance | None = None


class StoryCard(BaseModel):
    story_id: str
    title: str
    thumbnail: str
