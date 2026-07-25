from io import BytesIO
from pathlib import Path

from fastapi.testclient import TestClient
from PIL import Image
from sqlalchemy.engine import Engine

from services.api.main import create_app


def png_upload(mode: str = "RGB") -> tuple[str, BytesIO, str]:
    buffer = BytesIO()
    color: tuple[int, ...] = (255, 0, 0) if mode == "RGB" else (255, 0, 0, 128)
    Image.new(mode, (8, 6), color).save(buffer, format="PNG")
    buffer.seek(0)
    return ("product.png", buffer, "image/png")


def make_client(engine: Engine, tmp_path: Path) -> TestClient:
    return TestClient(create_app(engine, asset_root=tmp_path))


def create_project(client: TestClient) -> str:
    response = client.post("/api/projects", json={"name": "Upload Test"})
    return str(response.json()["id"])


def test_upload_product_image(engine: Engine, tmp_path: Path) -> None:
    with make_client(engine, tmp_path) as client:
        project_id = create_project(client)
        response = client.post(
            f"/api/projects/{project_id}/assets",
            data={"role": "product"},
            files={"file": png_upload()},
        )
    assert response.status_code == 201
    body = response.json()
    assert body["role"] == "product"
    assert body["mime"] == "image/png"
    assert (body["width"], body["height"]) == (8, 6)
    assert Path(body["path"]).exists()


def test_upload_unknown_project_404(engine: Engine, tmp_path: Path) -> None:
    with make_client(engine, tmp_path) as client:
        response = client.post(
            "/api/projects/nope/assets", data={"role": "product"}, files={"file": png_upload()}
        )
    assert response.status_code == 404


def test_upload_opaque_logo_422(engine: Engine, tmp_path: Path) -> None:
    with make_client(engine, tmp_path) as client:
        project_id = create_project(client)
        response = client.post(
            f"/api/projects/{project_id}/assets",
            data={"role": "logo"},
            files={"file": png_upload("RGB")},
        )
    assert response.status_code == 422


def test_upload_garbage_product_422(engine: Engine, tmp_path: Path) -> None:
    with make_client(engine, tmp_path) as client:
        project_id = create_project(client)
        response = client.post(
            f"/api/projects/{project_id}/assets",
            data={"role": "product"},
            files={"file": ("x.png", BytesIO(b"not an image"), "image/png")},
        )
    assert response.status_code == 422


def test_upload_derived_role_415(engine: Engine, tmp_path: Path) -> None:
    with make_client(engine, tmp_path) as client:
        project_id = create_project(client)
        response = client.post(
            f"/api/projects/{project_id}/assets",
            data={"role": "derived"},
            files={"file": png_upload()},
        )
    assert response.status_code == 415


def test_upload_brief_audio(engine: Engine, tmp_path: Path) -> None:
    with make_client(engine, tmp_path) as client:
        project_id = create_project(client)
        response = client.post(
            f"/api/projects/{project_id}/assets",
            data={"role": "brief_audio"},
            files={"file": ("brief.wav", BytesIO(b"RIFFxxxxWAVEfmt "), "audio/wav")},
        )
    assert response.status_code == 201
    assert response.json()["role"] == "brief_audio"


def test_upload_brief_audio_wrong_mime_415(engine: Engine, tmp_path: Path) -> None:
    with make_client(engine, tmp_path) as client:
        project_id = create_project(client)
        response = client.post(
            f"/api/projects/{project_id}/assets",
            data={"role": "brief_audio"},
            files={"file": ("b.mp4", BytesIO(b"data"), "video/mp4")},
        )
    assert response.status_code == 415
