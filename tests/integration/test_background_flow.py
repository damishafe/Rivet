from io import BytesIO
from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient
from PIL import Image
from sqlalchemy.engine import Engine

from rivet.adapters.background import BackgroundStage
from rivet.storage.events import EventStore
from services.api.main import create_app


def fake_generator(config: dict[str, Any], seed: int, device: str, out_path: Path) -> None:
    Image.new("RGB", (64, 96), (255, 90, 0)).save(out_path)


def upload(client: TestClient, project_id: str, role: str, mode: str) -> None:
    buffer = BytesIO()
    color: tuple[int, ...] = (255, 59, 0) if mode == "RGB" else (255, 59, 0, 200)
    Image.new(mode, (8, 8), color).save(buffer, format="PNG")
    buffer.seek(0)
    client.post(
        f"/api/projects/{project_id}/assets",
        data={"role": role},
        files={"file": (f"{role}.png", buffer, "image/png")},
    )


def build_app(engine: Engine, tmp_path: Path) -> TestClient:
    app = create_app(engine, asset_root=tmp_path)
    app.state.background_stage = BackgroundStage(generator=fake_generator)
    return TestClient(app)


def planned_project(client: TestClient) -> str:
    project_id = str(client.post("/api/projects", json={"name": "Kora"}).json()["id"])
    upload(client, project_id, "product", "RGB")
    upload(client, project_id, "logo", "RGBA")
    proposal = client.post(f"/api/projects/{project_id}/brand/derive").json()
    client.put(f"/api/projects/{project_id}/brand", json=proposal)
    client.post(f"/api/projects/{project_id}/plan")
    return project_id


def test_generate_backgrounds_runs_all_shots(engine: Engine, tmp_path: Path) -> None:
    with build_app(engine, tmp_path) as client:
        project_id = planned_project(client)
        response = client.post(f"/api/projects/{project_id}/generate/backgrounds")
    assert response.status_code == 202
    job = response.json()
    assert job["status"] == "succeeded"
    events = EventStore(engine).list_after(job["id"])
    statuses = [e.status for _, e in events]
    assert statuses == ["running", "succeeded"] * 3
    work = tmp_path / "projects" / project_id / "work" / job["id"]
    assert {p.name for p in work.glob("*.png")} == {"hook.png", "proof.png", "cta.png"}


def test_generate_backgrounds_without_plan_409(engine: Engine, tmp_path: Path) -> None:
    with build_app(engine, tmp_path) as client:
        project_id = str(client.post("/api/projects", json={"name": "Bare"}).json()["id"])
        response = client.post(f"/api/projects/{project_id}/generate/backgrounds")
    assert response.status_code == 409
