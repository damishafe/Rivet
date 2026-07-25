import asyncio
import shutil
from pathlib import Path

import pytest
from PIL import Image

from rivet.adapters.motion import MotionStage
from rivet.pipeline.stage import StageContext, StageRequest

ffmpeg_missing = shutil.which("ffmpeg") is None


def make_context(tmp_path: Path) -> StageContext:
    workdir = tmp_path / "work"
    workdir.mkdir()
    return StageContext(project_id="p1", job_id="j1", workdir=workdir)


@pytest.mark.skipif(ffmpeg_missing, reason="requires ffmpeg")
def test_motion_produces_clip(tmp_path: Path) -> None:
    still = tmp_path / "hook-still.png"
    Image.new("RGB", (1080, 1920), (40, 40, 44)).save(still)
    request = StageRequest(
        stage="motion.hook",
        seed=1,
        config={"shot_id": "hook", "still_path": str(still), "duration_s": 2.0},
    )
    result = asyncio.run(MotionStage().run(make_context(tmp_path), request))
    clip = Path(result.artifacts["clip"])
    assert clip.name == "hook.mp4"
    assert clip.exists()
    assert result.metrics["duration_s"] == 2.0


def test_estimate_resources_is_cpu() -> None:
    plan = MotionStage().estimate_resources(StageRequest(stage="motion", seed=1))
    assert plan.prefers_gpu is False
