from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from rivet.domain.ids import new_id
from rivet.domain.models import utcnow


class GpuSample(BaseModel):
    vram_used_mb: int
    utilization_pct: int


class StageEvent(BaseModel):
    event_id: str = Field(default_factory=new_id)
    job_id: str
    project_id: str
    stage: str
    shot_id: str | None = None
    status: Literal["queued", "running", "succeeded", "failed", "cancelled"]
    progress: float = Field(ge=0, le=1)
    elapsed_ms: int = 0
    gpu: GpuSample | None = None
    message: str = ""
    timestamp: datetime = Field(default_factory=utcnow)
