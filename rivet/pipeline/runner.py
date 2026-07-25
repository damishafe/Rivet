from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from sqlalchemy.engine import Engine

from rivet.domain.events import StageEvent
from rivet.domain.jobs import Job
from rivet.domain.models import StageRun, utcnow
from rivet.pipeline.stage import ModelManifest, Stage, StageContext, StageRequest, StageResult
from rivet.storage.events import EventStore
from rivet.storage.jobs import JobStore
from rivet.storage.stage_cache import StageCacheStore
from rivet.storage.stage_runs import StageRunStore


@dataclass
class PlannedStage:
    stage: Stage
    request: StageRequest
    manifest: ModelManifest | None = None


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
            return await self._execute(job, plan, workdir)
        except Exception as error:
            failed = self._jobs.set_status(job.id, "failed", error=str(error))
            self._emit(job, "runner", "failed", 0.0, str(error))
            return failed

    async def _execute(
        self, job: Job, plan: list[PlannedStage], workdir: Path | None = None
    ) -> Job:
        if workdir is None:
            workdir = self._asset_root / "projects" / job.project_id / "work" / job.id
        workdir.mkdir(parents=True, exist_ok=True)
        context = StageContext(project_id=job.project_id, job_id=job.id, workdir=workdir)
        total = len(plan)
        for index, planned in enumerate(plan):
            if self._jobs.cancel_requested(job.id):
                self._emit(job, planned.request.stage, "cancelled", index / total)
                return self._jobs.set_status(job.id, "cancelled")
            raw_fingerprint = planned.stage.fingerprint(planned.request, planned.manifest)
            fingerprint = f"{planned.request.stage}:{raw_fingerprint}"
            self._emit(job, planned.request.stage, "running", index / total)
            started = utcnow()
            cached = self._cache.get(fingerprint)
            if cached is not None:
                result: StageResult | None = cached
            else:
                try:
                    result = await planned.stage.run(context, planned.request)
                except Exception as error:
                    self._record(job, planned, started, "failed", cache_hit=False)
                    self._emit(job, planned.request.stage, "failed", index / total, str(error))
                    return self._jobs.set_status(job.id, "failed", error=str(error))
                finally:
                    await planned.stage.cleanup()
                self._cache.put(fingerprint, result)
            self._record(job, planned, started, "succeeded", cache_hit=cached is not None)
            self._emit(job, planned.request.stage, "succeeded", (index + 1) / total)
        return self._jobs.set_status(job.id, "succeeded")

    def _record(
        self,
        job: Job,
        planned: PlannedStage,
        started_at: datetime,
        status: str,
        cache_hit: bool,
    ) -> None:
        self._runs.add(
            StageRun.model_validate(
                {
                    "project_id": job.project_id,
                    "job_id": job.id,
                    "stage": planned.request.stage,
                    "model": planned.manifest.repo if planned.manifest else None,
                    "revision": planned.manifest.revision if planned.manifest else None,
                    "dtype": planned.manifest.dtype if planned.manifest else None,
                    "seed": planned.request.seed,
                    "started_at": started_at,
                    "finished_at": utcnow(),
                    "status": status,
                    "cache_hit": cache_hit,
                }
            )
        )
