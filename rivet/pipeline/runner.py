import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Literal

from sqlalchemy.engine import Engine

from rivet.domain.events import StageEvent
from rivet.domain.jobs import Job
from rivet.domain.models import StageRun, utcnow
from rivet.pipeline.stage import ModelManifest, Stage, StageContext, StageRequest, StageResult
from rivet.storage.events import EventStore
from rivet.storage.jobs import JobStore
from rivet.storage.stage_cache import StageCacheStore
from rivet.storage.stage_runs import StageRunStore
from rivet.telemetry.vram import peak_mb, reset_peak


@dataclass
class PlannedStage:
    stage: Stage
    request: StageRequest
    manifest: ModelManifest | None = None
    input_paths: list[str] = field(default_factory=list)


@dataclass
class PhaseOutcome:
    status: Literal["succeeded", "failed", "cancelled"]
    error: str | None = None


class JobRunner:
    def __init__(self, engine: Engine, asset_root: Path) -> None:
        self._jobs = JobStore(engine)
        self._events = EventStore(engine)
        self._runs = StageRunStore(engine)
        self._cache = StageCacheStore(engine)
        self._asset_root = asset_root

    def _emit(
        self, job: Job, stage: str, status: str, progress: float, message: str = ""
    ) -> None:
        self._events.append(
            StageEvent.model_validate(
                {
                    "job_id": job.id,
                    "project_id": job.project_id,
                    "stage": stage,
                    "status": status,
                    "progress": progress,
                    "message": message or stage,
                }
            )
        )

    async def run(
        self, job: Job, plan: list[PlannedStage], workdir: Path | None = None
    ) -> Job:
        self._jobs.set_status(job.id, "running")
        try:
            outcome = await self.run_phase(job, plan, workdir)
        except Exception as error:
            failed = self._jobs.set_status(job.id, "failed", error=str(error))
            self._emit(job, "runner", "failed", 0.0, str(error))
            return failed
        if outcome.status == "succeeded":
            return self._jobs.set_status(job.id, "succeeded")
        return self._jobs.set_status(job.id, outcome.status, error=outcome.error)

    def _resolved_request(self, planned: PlannedStage) -> StageRequest:
        digests = [
            hashlib.sha256(Path(path).read_bytes()).hexdigest()
            for path in planned.input_paths
            if Path(path).is_file()
        ]
        if not digests:
            return planned.request
        return planned.request.model_copy(
            update={"input_hashes": [*planned.request.input_hashes, *digests]}
        )

    async def run_phase(
        self, job: Job, plan: list[PlannedStage], workdir: Path | None = None
    ) -> PhaseOutcome:
        if workdir is None:
            workdir = self._asset_root / "projects" / job.project_id / "work" / job.id
        workdir.mkdir(parents=True, exist_ok=True)
        context = StageContext(project_id=job.project_id, job_id=job.id, workdir=workdir)
        total = max(len(plan), 1)
        for index, planned in enumerate(plan):
            if self._jobs.cancel_requested(job.id):
                self._emit(job, planned.request.stage, "cancelled", index / total)
                return PhaseOutcome("cancelled")
            request = self._resolved_request(planned)
            fingerprint = f"{request.stage}:{planned.stage.fingerprint(request, planned.manifest)}"
            self._emit(job, request.stage, "running", index / total)
            started = utcnow()
            cached = self._cache.get(fingerprint)
            peak: int | None = None
            if cached is not None:
                result: StageResult | None = cached
            else:
                reset_peak()
                try:
                    result = await planned.stage.run(context, request)
                except Exception as error:
                    self._record(job, planned, request, started, "failed", False, peak_mb())
                    self._emit(job, request.stage, "failed", index / total, str(error))
                    return PhaseOutcome("failed", str(error))
                finally:
                    await planned.stage.cleanup()
                peak = peak_mb()
                self._cache.put(fingerprint, result)
            self._record(
                job, planned, request, started, "succeeded", cached is not None, peak
            )
            self._emit(job, request.stage, "succeeded", (index + 1) / total)
        return PhaseOutcome("succeeded")

    def _record(
        self,
        job: Job,
        planned: PlannedStage,
        request: StageRequest,
        started_at: datetime,
        status: str,
        cache_hit: bool,
        peak_vram_mb: int | None,
    ) -> None:
        self._runs.add(
            StageRun.model_validate(
                {
                    "project_id": job.project_id,
                    "job_id": job.id,
                    "stage": request.stage,
                    "model": planned.manifest.repo if planned.manifest else None,
                    "revision": planned.manifest.revision if planned.manifest else None,
                    "dtype": planned.manifest.dtype if planned.manifest else None,
                    "seed": request.seed,
                    "started_at": started_at,
                    "finished_at": utcnow(),
                    "peak_vram_mb": peak_vram_mb,
                    "status": status,
                    "cache_hit": cache_hit,
                }
            )
        )
