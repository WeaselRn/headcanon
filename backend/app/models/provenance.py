from datetime import datetime

from pydantic import BaseModel


class Provenance(BaseModel):
    execution_id: str
    pipeline_version: str
    models_used: list[str]
    started_at: datetime
    completed_at: datetime
    assets_generated: list[str]
