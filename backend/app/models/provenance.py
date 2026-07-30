from datetime import datetime

from pydantic import BaseModel, Field


class Provenance(BaseModel):
    execution_id: str
    pipeline_version: str
    models_used: list[str]
    started_at: datetime
    completed_at: datetime
    assets_generated: list[str]
    status: str = "completed"
    storage_locations: list[str] = Field(default_factory=list)
