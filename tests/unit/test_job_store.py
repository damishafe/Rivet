import pytest
from sqlalchemy.engine import Engine

from rivet.domain.models import StageRun, utcnow
from rivet.storage.jobs import ActiveJobError, JobStore
from rivet.storage.stage_runs import StageRunStore


def test_create_and_get_round_trip(engine: Engine) -> None:
    store = JobStore(engine)
    job = store.create("p1", "generate")
    assert store.get(job.id) == job
    assert job.status == "queued"


def test_second_active_job_rejected(engine: Engine) -> None:
    store = JobStore(engine)
    store.create("p1", "generate")
    with pytest.raises(ActiveJobError):
        store.create("p1", "generate")


def test_finished_job_allows_new_one(engine: Engine) -> None:
    store = JobStore(engine)
    first = store.create("p1", "generate")
    store.set_status(first.id, "succeeded")
    second = store.create("p1", "generate")
    assert second.id != first.id


def test_set_status_records_error(engine: Engine) -> None:
    store = JobStore(engine)
    job = store.create("p1", "generate")
    failed = store.set_status(job.id, "failed", error="boom")
    assert (failed.status, failed.error) == ("failed", "boom")


def test_cancel_flag_round_trip(engine: Engine) -> None:
    store = JobStore(engine)
    job = store.create("p1", "generate")
    assert store.cancel_requested(job.id) is False
    store.request_cancel(job.id)
    assert store.cancel_requested(job.id) is True


def test_unknown_job_raises(engine: Engine) -> None:
    store = JobStore(engine)
    with pytest.raises(KeyError):
        store.set_status("missing", "running")
    with pytest.raises(KeyError):
        store.request_cancel("missing")


def test_stage_runs_ordered_per_job(engine: Engine) -> None:
    runs = StageRunStore(engine)
    first = StageRun(
        project_id="p1", job_id="j1", stage="a", seed=1,
        started_at=utcnow(), status="succeeded",
    )
    second = StageRun(
        project_id="p1", job_id="j1", stage="b", seed=1,
        started_at=utcnow(), status="succeeded",
    )
    runs.add(first)
    runs.add(second)
    listed = runs.list_for_job("j1")
    assert [r.stage for r in listed] == ["a", "b"]
    assert runs.list_for_job("other") == []
