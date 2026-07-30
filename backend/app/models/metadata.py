from datetime import datetime

from pydantic import BaseModel


class StoryMetadata(BaseModel):
    created_at: datetime
    updated_at: datetime
    models: list[str]
    pipeline_version: str
