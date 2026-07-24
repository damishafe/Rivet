from fastapi.testclient import TestClient
from sqlalchemy.engine import Engine

from rivet.domain.events import StageEvent
from rivet.storage.events import EventStore
from rivet.storage.jobs import JobStore
from services.api.main import create_app


def seed_events(engine: Engine, count: int) -> None:
    store = EventStore(engine)
    for i in range(count):
        store.append(
            StageEvent(
                job_id="job-1", project_id="p1", stage="background.generate",
                status="running", progress=i / count, message=f"step {i}",
            )
        )


def test_replay_streams_all_events_and_closes(engine: Engine) -> None:
    seed_events(engine, 3)
    with TestClient(create_app(engine)) as client:
        response = client.get("/api/jobs/job-1/events?follow=false")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    body = response.text
    assert body.count("event: stage") == 3
    assert "step 0" in body and "step 2" in body
    assert "id: 3" in body


def test_after_skips_consumed_events(engine: Engine) -> None:
    seed_events(engine, 3)
    with TestClient(create_app(engine)) as client:
        response = client.get("/api/jobs/job-1/events?follow=false&after=2")
    assert response.text.count("event: stage") == 1
    assert "step 2" in response.text


def test_unknown_job_replays_nothing(engine: Engine) -> None:
    with TestClient(create_app(engine)) as client:
        response = client.get("/api/jobs/ghost/events?follow=false")
    assert response.status_code == 200
    assert "event: stage" not in response.text


def test_last_event_id_header_resumes_stream(engine: Engine) -> None:
    seed_events(engine, 3)
    with TestClient(create_app(engine)) as client:
        response = client.get(
            "/api/jobs/job-1/events?follow=false", headers={"last-event-id": "2"}
        )
    assert response.text.count("event: stage") == 1
    assert "step 2" in response.text


def test_get_job_and_cancel(engine: Engine) -> None:
    job = JobStore(engine).create("p1", "generate")
    with TestClient(create_app(engine)) as client:
        fetched = client.get(f"/api/jobs/{job.id}")
        assert fetched.status_code == 200
        assert fetched.json()["status"] == "queued"
        cancelled = client.post(f"/api/jobs/{job.id}/cancel")
    assert cancelled.status_code == 202
    assert JobStore(engine).cancel_requested(job.id) is True


def test_unknown_job_404(engine: Engine) -> None:
    with TestClient(create_app(engine)) as client:
        assert client.get("/api/jobs/nope").status_code == 404
        assert client.post("/api/jobs/nope/cancel").status_code == 404
