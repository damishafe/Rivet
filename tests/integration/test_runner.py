import asyncio
from dataclasses import dataclass, field
from pathlib import Path

from sqlalchemy.engine import Engine

from rivet.pipeline.fingerprint import cache_key
from rivet.pipeline.runner import JobRunner, PlannedStage
from rivet.pipeline.stage import (
    ModelManifest,
    ResourcePlan,
    StageContext,
    StageRequest,
    StageResult,
)
from rivet.storage.events import EventStore
from rivet.storage.jobs import JobStore
from rivet.storage.stage_runs import StageRunStore


@dataclass
class EchoStage:
    name: str = "echo"
    version: str = "1"
    calls: list[str] = field(default_factory=list)

    def fingerprint(self, request: StageRequest, manifest: ModelManifest | None) -> str:
        return cache_key(self.name, self.version, request, manifest)

    def estimate_resources(self, request: StageRequest) -> ResourcePlan:
        return ResourcePlan(est_vram_mb=0, prefers_gpu=False)

    async def run(self, context: StageContext, request: StageRequest) -> StageResult:
        self.calls.append(request.stage)
        out = context.workdir / f"{request.stage}.txt"
        out.write_text(request.stage)
        return StageResult(artifacts={"out": str(out)})

    async def cleanup(self) -> None:
        return None


@dataclass
class BoomStage(EchoStage):
    name: str = "boom"

    async def run(self, context: StageContext, request: StageRequest) -> StageResult:
        raise RuntimeError("boom")


def make_plan(stage: EchoStage, names: list[str]) -> list[PlannedStage]:
    return [
        PlannedStage(stage=stage, request=StageRequest(stage=name, seed=7))
        for name in names
    ]


def test_successful_job_emits_events_and_runs(engine: Engine, tmp_path: Path) -> None:
    jobs = JobStore(engine)
    job = jobs.create("p1", "generate")
    stage = EchoStage()
    runner = JobRunner(engine, tmp_path)
    finished = asyncio.run(runner.run(job, make_plan(stage, ["one", "two"])))
    assert finished.status == "succeeded"
    assert stage.calls == ["one", "two"]
    events = EventStore(engine).list_after(job.id)
    statuses = [event.status for _, event in events]
    assert statuses == ["running", "succeeded", "running", "succeeded"]
    assert events[-1][1].progress == 1.0
    runs = StageRunStore(engine).list_for_job(job.id)
    assert [run.status for run in runs] == ["succeeded", "succeeded"]


def test_failure_marks_job_and_emits_failed(engine: Engine, tmp_path: Path) -> None:
    jobs = JobStore(engine)
    job = jobs.create("p1", "generate")
    finished = asyncio.run(
        JobRunner(engine, tmp_path).run(job, make_plan(BoomStage(), ["only"]))
    )
    assert finished.status == "failed"
    assert finished.error == "boom"
    events = EventStore(engine).list_after(job.id)
    assert events[-1][1].status == "failed"
    runs = StageRunStore(engine).list_for_job(job.id)
    assert runs[-1].status == "failed"


def test_cancel_before_start_skips_stages(engine: Engine, tmp_path: Path) -> None:
    jobs = JobStore(engine)
    job = jobs.create("p1", "generate")
    jobs.request_cancel(job.id)
    stage = EchoStage()
    finished = asyncio.run(JobRunner(engine, tmp_path).run(job, make_plan(stage, ["one"])))
    assert finished.status == "cancelled"
    assert stage.calls == []
    events = EventStore(engine).list_after(job.id)
    assert events[-1][1].status == "cancelled"


def test_second_job_hits_cache(engine: Engine, tmp_path: Path) -> None:
    jobs = JobStore(engine)
    stage = EchoStage()
    first = jobs.create("p1", "generate")
    asyncio.run(JobRunner(engine, tmp_path).run(first, make_plan(stage, ["one"])))
    second = jobs.create("p1", "generate")
    asyncio.run(JobRunner(engine, tmp_path).run(second, make_plan(stage, ["one"])))
    assert stage.calls == ["one"]
    runs = StageRunStore(engine).list_for_job(second.id)
    assert runs[0].cache_hit is True
    refreshed = JobStore(engine).get(second.id)
    assert refreshed is not None and refreshed.status == "succeeded"
