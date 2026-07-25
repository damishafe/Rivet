import shutil
from io import BytesIO
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient
from PIL import Image, ImageDraw
from sqlalchemy.engine import Engine

from rivet.adapters.background import BackgroundStage
from rivet.adapters.segment import SegmentStage
from services.api.main import create_app

ffmpeg_missing = shutil.which("ffmpeg") is None


def fake_segmenter(image_path: str, config: dict[str, Any], device: str, out_path: Path) -> float:
    cutout = Image.new("RGBA", (500, 600), (0, 0, 0, 0))
    ImageDraw.Draw(cutout).rounded_rectangle([30, 30, 470, 570], radius=48, fill=(40, 40, 44, 255))
    cutout.save(out_path)
    return 0.98


def fake_background(config: dict[str, Any], seed: int, device: str, out_path: Path) -> None:
    Image.new("RGB", (768, 1344), (44, 40, 32)).save(out_path)


def upload(client: TestClient, project_id: str, role: str, image: Image.Image) -> None:
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    client.post(
        f"/api/projects/{project_id}/assets",
        data={"role": role},
        files={"file": (f"{role}.png", buffer, "image/png")},
    )


def build_app(engine: Engine, tmp_path: Path) -> TestClient:
    app = create_app(engine, asset_root=tmp_path)
    app.state.segment_stage = SegmentStage(segmenter=fake_segmenter)
    app.state.background_stage = BackgroundStage(generator=fake_background)
    return TestClient(app)


def planned_project(client: TestClient) -> str:
    project_id = str(client.post("/api/projects", json={"name": "Kora"}).json()["id"])
    upload(client, project_id, "product", Image.new("RGB", (16, 16), (255, 59, 0)))
    upload(client, project_id, "logo", Image.new("RGBA", (80, 24), (250, 250, 250, 255)))
    proposal = client.post(f"/api/projects/{project_id}/brand/derive").json()
    client.put(f"/api/projects/{project_id}/brand", json=proposal)
    client.post(f"/api/projects/{project_id}/plan")
    return project_id


@pytest.mark.skipif(ffmpeg_missing, reason="requires ffmpeg")
def test_campaign_produces_passing_receipt(engine: Engine, tmp_path: Path) -> None:
    with build_app(engine, tmp_path) as client:
        project_id = planned_project(client)
        response = client.post(f"/api/projects/{project_id}/generate/campaign")
    assert response.status_code == 200, response.text
    receipt = response.json()
    assert receipt["passed"] is True
    assert [s["shot_id"] for s in receipt["scenes"]] == ["hook", "proof", "cta"]
    assert all(len(s["checks"]) == 7 for s in receipt["scenes"])
    assert len(receipt["receipt_hash"]) == 64
    assert receipt["video_path"] and Path(receipt["video_path"]).exists()
    saved = tmp_path / "projects" / project_id / "work"
    assert any(p.name == "receipt.json" for p in saved.rglob("receipt.json"))


def test_campaign_without_plan_409(engine: Engine, tmp_path: Path) -> None:
    with build_app(engine, tmp_path) as client:
        project_id = str(client.post("/api/projects", json={"name": "Bare"}).json()["id"])
        response = client.post(f"/api/projects/{project_id}/generate/campaign")
    assert response.status_code == 409
