from pathlib import Path
from typing import Any, Protocol

from pydantic import BaseModel, Field


class StageRequest(BaseModel):
    stage: str
    config: dict[str, Any] = Field(default_factory=dict)
    seed: int
    input_hashes: list[str] = Field(default_factory=list)


class StageResult(BaseModel):
    artifacts: dict[str, str] = Field(default_factory=dict)
    metrics: dict[str, float] = Field(default_factory=dict)
    evidence: dict[str, str] = Field(default_factory=dict)
    checkpoint: str | None = None


class ResourcePlan(BaseModel):
    est_vram_mb: int
    prefers_gpu: bool = True


class ModelManifest(BaseModel):
    repo: str
    revision: str
    dtype: str


class StageContext(BaseModel):
    project_id: str
    job_id: str
    workdir: Path


class Stage(Protocol):
    name: str
    version: str

    def fingerprint(self, request: StageRequest, manifest: ModelManifest | None) -> str: ...

    def estimate_resources(self, request: StageRequest) -> ResourcePlan: ...

    async def run(self, context: StageContext, request: StageRequest) -> StageResult: ...

    async def cleanup(self) -> None: ...
