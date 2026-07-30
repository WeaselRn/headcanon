from pydantic import BaseModel

from app.models.story import Story, StoryCard


class StoryResponse(Story):
    pass


class StoryListResponse(BaseModel):
    stories: list[StoryCard]


class RegenerateSceneResponse(BaseModel):
    image_url: str


class ErrorResponse(BaseModel):
    error: str


class HealthResponse(BaseModel):
    status: str
