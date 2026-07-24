from sqlalchemy import inspect
from sqlalchemy.engine import Engine

from rivet.domain.jobs import Job
from rivet.domain.models import StageRun, utcnow


def test_job_defaults() -> None:
    job = Job(project_id="p1", kind="generate")
    assert job.status == "queued"
    assert job.error is None
    assert len(job.id) == 32


def test_stage_run_carries_job_id() -> None:
    run = StageRun(
        project_id="p1", job_id="j1", stage="echo", seed=1,
        started_at=utcnow(), status="running",
    )
    assert run.job_id == "j1"


def test_new_tables_exist(engine: Engine) -> None:
    tables = set(inspect(engine).get_table_names())
    assert {"jobs", "stage_runs"} <= tables
