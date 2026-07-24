from sqlalchemy.engine import Engine

from rivet.domain.events import StageEvent
from rivet.storage.events import EventStore


def make_event(job_id: str, message: str) -> StageEvent:
    return StageEvent(
        job_id=job_id, project_id="p1", stage="test.stage", status="running",
        progress=0.5, message=message,
    )


def test_append_assigns_monotonic_seq_per_job(engine: Engine) -> None:
    store = EventStore(engine)
    assert store.append(make_event("job-a", "one")) == 1
    assert store.append(make_event("job-a", "two")) == 2
    assert store.append(make_event("job-b", "other")) == 1


def test_list_after_replays_in_order(engine: Engine) -> None:
    store = EventStore(engine)
    for message in ("one", "two", "three"):
        store.append(make_event("job-a", message))
    replayed = store.list_after("job-a")
    assert [seq for seq, _ in replayed] == [1, 2, 3]
    assert [event.message for _, event in replayed] == ["one", "two", "three"]


def test_list_after_skips_consumed_events(engine: Engine) -> None:
    store = EventStore(engine)
    for message in ("one", "two", "three"):
        store.append(make_event("job-a", message))
    replayed = store.list_after("job-a", after_seq=2)
    assert [event.message for _, event in replayed] == ["three"]


def test_list_after_unknown_job_is_empty(engine: Engine) -> None:
    assert EventStore(engine).list_after("nope") == []
