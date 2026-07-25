from io import BytesIO
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy.engine import Engine

from rivet.adapters.transcribe import TranscribeStage
from rivet.storage.events import EventStore
from services.api.main import create_app


def build_app(engine: Engine, tmp_path: Path) -> TestClient:
    app = create_app(engine, asset_root=tmp_path)
    app.state.transcribe_stage = TranscribeStage(
        transcriber=lambda path, device: "make every space your studio"
    )
    return TestClient(app)


def test_transcribe_runs_through_runner(engine: Engine, tmp_path: Path) -> None:
    with build_app(engine, tmp_path) as client:
        project_id = str(client.post("/api/projects", json={"name": "Kora"}).json()["id"])
        client.post(
            f"/api/projects/{project_id}/assets",
            data={"role": "brief_audio"},
            files={"file": ("b.wav", BytesIO(b"RIFFxxxxWAVEfmt "), "audio/wav")},
        )
        response = client.post(f"/api/projects/{project_id}/transcribe")
    assert response.status_code == 202
    job = response.json()
    assert job["status"] == "succeeded"
    events = EventStore(engine).list_after(job["id"])
    assert [e.status for _, e in events] == ["running", "succeeded"]
    work = tmp_path / "projects" / project_id / "work" / job["id"] / "transcript.txt"
    assert work.read_text() == "make every space your studio"


def test_transcribe_without_audio_409(engine: Engine, tmp_path: Path) -> None:
    with build_app(engine, tmp_path) as client:
        project_id = str(client.post("/api/projects", json={"name": "Bare"}).json()["id"])
        response = client.post(f"/api/projects/{project_id}/transcribe")
    assert response.status_code == 409
