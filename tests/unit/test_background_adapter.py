import asyncio
from pathlib import Path
from typing import Any

from PIL import Image

from rivet.adapters.background import BackgroundStage
from rivet.pipeline.stage import ModelManifest, StageContext, StageRequest


def make_context(tmp_path: Path) -> StageContext:
    workdir = tmp_path / "work"
    workdir.mkdir()
    return StageContext(project_id="p1", job_id="j1", workdir=workdir)


def fake_generator(config: dict[str, Any], seed: int, device: str, out_path: Path) -> None:
    width = int(config.get("width", 832))
    height = int(config.get("height", 1216))
    Image.new("RGB", (width, height), (255, 90, 0)).save(out_path)


def make_request(shot_id: str = "hook", **config: Any) -> StageRequest:
    base: dict[str, Any] = {"shot_id": shot_id, "prompt": "a studio backdrop"}
    base.update(config)
    return StageRequest(stage=f"background.{shot_id}", seed=7, config=base)


def test_writes_plate_named_by_shot(tmp_path: Path) -> None:
    stage = BackgroundStage(generator=fake_generator)
    result = asyncio.run(stage.run(make_context(tmp_path), make_request("proof")))
    plate = Path(result.artifacts["plate"])
    assert plate.name == "proof.png"
    assert plate.exists()
    assert Image.open(plate).size == (832, 1216)


def test_metrics_report_dimensions(tmp_path: Path) -> None:
    stage = BackgroundStage(generator=fake_generator)
    result = asyncio.run(stage.run(make_context(tmp_path), make_request(width=768, height=1344)))
    assert result.metrics == {"width": 768.0, "height": 1344.0}


def test_fingerprint_differs_per_shot() -> None:
    stage = BackgroundStage(generator=fake_generator)
    manifest = ModelManifest(repo="sdxl", revision="r1", dtype="fp16")
    hook = stage.fingerprint(make_request("hook"), manifest)
    proof = stage.fingerprint(make_request("proof"), manifest)
    assert hook != proof
