import asyncio
from pathlib import Path
from typing import Any

from PIL import Image

from rivet.adapters.segment import SegmentStage
from rivet.pipeline.stage import StageContext, StageRequest


def make_context(tmp_path: Path) -> StageContext:
    workdir = tmp_path / "work"
    workdir.mkdir()
    return StageContext(project_id="p1", job_id="j1", workdir=workdir)


def fake_segmenter(image_path: str, config: dict[str, Any], device: str, out_path: Path) -> float:
    Image.new("RGBA", (32, 32), (255, 90, 0, 255)).save(out_path)
    return 0.97


def test_writes_cutout_and_confidence(tmp_path: Path) -> None:
    product = tmp_path / "product.png"
    Image.new("RGB", (32, 32), (255, 90, 0)).save(product)
    stage = SegmentStage(segmenter=fake_segmenter)
    request = StageRequest(stage="segmentation", seed=1, config={"image_path": str(product)})
    result = asyncio.run(stage.run(make_context(tmp_path), request))
    cutout = Path(result.artifacts["cutout"])
    assert cutout.name == "cutout.png"
    assert Image.open(cutout).mode == "RGBA"
    assert result.metrics["confidence"] == 0.97


def test_estimate_resources_is_light() -> None:
    plan = SegmentStage(segmenter=fake_segmenter).estimate_resources(
        StageRequest(stage="segmentation", seed=1)
    )
    assert plan.est_vram_mb <= 4000
