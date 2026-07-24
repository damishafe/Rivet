from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from rivet.domain.ids import new_id
from rivet.domain.models import utcnow

JobStatus = Literal["queued", "running", "succeeded", "failed", "cancelled"]


class Job(BaseModel):
    id: str = Field(default_factory=new_id)
    project_id: str
    kind: str
    status: JobStatus = "queued"
    error: str | None = None
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)
