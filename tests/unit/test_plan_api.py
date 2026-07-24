from io import BytesIO
from pathlib import Path

from fastapi.testclient import TestClient
from PIL import Image
from sqlalchemy.engine import Engine

from services.api.main import create_app


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


def planned_project(client: TestClient) -> str:
    project_id = str(client.post("/api/projects", json={"name": "Kora Arc"}).json()["id"])
    upload(client, project_id, "product", "RGB")
    upload(client, project_id, "logo", "RGBA")
    proposal = client.post(f"/api/projects/{project_id}/brand/derive").json()
    client.put(f"/api/projects/{project_id}/brand", json=proposal)
    return project_id


def test_derive_plan_returns_three_shots(engine: Engine, tmp_path: Path) -> None:
    with TestClient(create_app(engine, asset_root=tmp_path)) as client:
        project_id = planned_project(client)
        response = client.post(f"/api/projects/{project_id}/plan")
    assert response.status_code == 200
    shots = response.json()["shots"]
    assert [s["shot_id"] for s in shots] == ["hook", "proof", "cta"]


def test_derive_plan_without_brand_409(engine: Engine, tmp_path: Path) -> None:
    with TestClient(create_app(engine, asset_root=tmp_path)) as client:
        project_id = str(client.post("/api/projects", json={"name": "Bare"}).json()["id"])
        response = client.post(f"/api/projects/{project_id}/plan")
    assert response.status_code == 409


def test_get_plan_after_derive(engine: Engine, tmp_path: Path) -> None:
    with TestClient(create_app(engine, asset_root=tmp_path)) as client:
        project_id = planned_project(client)
        client.post(f"/api/projects/{project_id}/plan")
        response = client.get(f"/api/projects/{project_id}/plan")
    assert response.status_code == 200
    assert len(response.json()["shots"]) == 3


def test_get_plan_before_derive_404(engine: Engine, tmp_path: Path) -> None:
    with TestClient(create_app(engine, asset_root=tmp_path)) as client:
        project_id = planned_project(client)
        response = client.get(f"/api/projects/{project_id}/plan")
    assert response.status_code == 404


def test_edit_shot_persists(engine: Engine, tmp_path: Path) -> None:
    with TestClient(create_app(engine, asset_root=tmp_path)) as client:
        project_id = planned_project(client)
        shots = client.post(f"/api/projects/{project_id}/plan").json()["shots"]
        hook = shots[0]
        hook["copy"]["headline"] = "Brand New Headline"
        response = client.put(f"/api/projects/{project_id}/shots/hook", json=hook)
        assert response.status_code == 200
        stored = client.get(f"/api/projects/{project_id}/plan").json()["shots"]
    assert stored[0]["copy"]["headline"] == "Brand New Headline"


def test_edit_shot_id_mismatch_422(engine: Engine, tmp_path: Path) -> None:
    with TestClient(create_app(engine, asset_root=tmp_path)) as client:
        project_id = planned_project(client)
        shots = client.post(f"/api/projects/{project_id}/plan").json()["shots"]
        response = client.put(f"/api/projects/{project_id}/shots/proof", json=shots[0])
    assert response.status_code == 422


def test_edit_breaking_window_422(engine: Engine, tmp_path: Path) -> None:
    with TestClient(create_app(engine, asset_root=tmp_path)) as client:
        project_id = planned_project(client)
        shots = client.post(f"/api/projects/{project_id}/plan").json()["shots"]
        hook = shots[0]
        hook["duration_s"] = 40
        response = client.put(f"/api/projects/{project_id}/shots/hook", json=hook)
    assert response.status_code == 422


def test_edit_invalid_layout_422(engine: Engine, tmp_path: Path) -> None:
    with TestClient(create_app(engine, asset_root=tmp_path)) as client:
        project_id = planned_project(client)
        shots = client.post(f"/api/projects/{project_id}/plan").json()["shots"]
        hook = shots[0]
        hook["layout_template"] = "fancy_grid"
        response = client.put(f"/api/projects/{project_id}/shots/hook", json=hook)
    assert response.status_code == 422


def test_derive_frozen_after_generation_409(engine: Engine, tmp_path: Path) -> None:
    from rivet.domain.states import ProjectStatus
    from rivet.storage.projects import ProjectStore

    with TestClient(create_app(engine, asset_root=tmp_path)) as client:
        project_id = planned_project(client)
        client.post(f"/api/projects/{project_id}/plan")
        ProjectStore(engine).advance(project_id, ProjectStatus.GENERATING)
        response = client.post(f"/api/projects/{project_id}/plan")
    assert response.status_code == 409


def test_edit_frozen_after_generation_409(engine: Engine, tmp_path: Path) -> None:
    from rivet.domain.states import ProjectStatus
    from rivet.storage.projects import ProjectStore

    with TestClient(create_app(engine, asset_root=tmp_path)) as client:
        project_id = planned_project(client)
        shots = client.post(f"/api/projects/{project_id}/plan").json()["shots"]
        ProjectStore(engine).advance(project_id, ProjectStatus.GENERATING)
        response = client.put(f"/api/projects/{project_id}/shots/hook", json=shots[0])
    assert response.status_code == 409
