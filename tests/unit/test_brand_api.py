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


def setup_project(client: TestClient) -> str:
    project_id = str(client.post("/api/projects", json={"name": "Kora Arc"}).json()["id"])
    upload(client, project_id, "product", "RGB")
    upload(client, project_id, "logo", "RGBA")
    return project_id


def test_derive_returns_unconfirmed_proposal(engine: Engine, tmp_path: Path) -> None:
    with TestClient(create_app(engine, asset_root=tmp_path)) as client:
        project_id = setup_project(client)
        response = client.post(f"/api/projects/{project_id}/brand/derive")
    assert response.status_code == 200
    body = response.json()
    assert body["product_name"] == "Kora Arc"
    assert body["confirmed_at"] is None
    assert len(body["palette"]) >= 1


def test_derive_without_assets_409(engine: Engine, tmp_path: Path) -> None:
    with TestClient(create_app(engine, asset_root=tmp_path)) as client:
        project_id = str(client.post("/api/projects", json={"name": "Bare"}).json()["id"])
        response = client.post(f"/api/projects/{project_id}/brand/derive")
    assert response.status_code == 409


def test_confirm_brand_advances_status(engine: Engine, tmp_path: Path) -> None:
    with TestClient(create_app(engine, asset_root=tmp_path)) as client:
        project_id = setup_project(client)
        proposal = client.post(f"/api/projects/{project_id}/brand/derive").json()
        proposal["audience"] = "campus creators"
        response = client.put(f"/api/projects/{project_id}/brand", json=proposal)
        assert response.status_code == 200
        assert response.json()["status"] == "brand_ready"
        stored = client.get(f"/api/projects/{project_id}/brand").json()
    assert stored["audience"] == "campus creators"
    assert stored["confirmed_at"] is not None


def test_get_brand_before_derive_404(engine: Engine, tmp_path: Path) -> None:
    with TestClient(create_app(engine, asset_root=tmp_path)) as client:
        project_id = str(client.post("/api/projects", json={"name": "None"}).json()["id"])
        response = client.get(f"/api/projects/{project_id}/brand")
    assert response.status_code == 404
