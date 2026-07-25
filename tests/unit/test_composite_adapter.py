import asyncio
from pathlib import Path

import pytest
from PIL import Image

from rivet.adapters.composite import CompositeStage
from rivet.pipeline.stage import StageContext, StageRequest


def make_inputs(tmp_path: Path) -> dict[str, str]:
    bg = tmp_path / "bg.png"
    Image.new("RGB", (400, 600), (50, 50, 55)).save(bg)
    cut = tmp_path / "cut.png"
    Image.new("RGBA", (120, 120), (255, 90, 0, 255)).save(cut)
    logo = tmp_path / "logo.png"
    Image.new("RGBA", (100, 32), (250, 250, 250, 255)).save(logo)
    return {"background_path": str(bg), "cutout_path": str(cut), "logo_path": str(logo)}


def make_context(tmp_path: Path) -> StageContext:
    workdir = tmp_path / "work"
    workdir.mkdir()
    return StageContext(project_id="p1", job_id="j1", workdir=workdir)


def test_composes_still_from_inputs(tmp_path: Path) -> None:
    config = make_inputs(tmp_path)
    config.update(
        {
            "shot_id": "hook",
            "layout": "center_hero",
            "headline": "Kora Arc",
            "support": "Make every space your studio",
            "cta": "Shop now",
            "accent": [255, 59, 0],
        }
    )
    request = StageRequest(stage="composite.hook", seed=1, config=config)
    result = asyncio.run(CompositeStage().run(make_context(tmp_path), request))
    still = Path(result.artifacts["still"])
    assert still.name == "hook-still.png"
    image = Image.open(still)
    assert image.size == (1080, 1920)
    assert result.metrics == {"width": 1080.0, "height": 1920.0}


def test_unknown_layout_raises(tmp_path: Path) -> None:
    config = make_inputs(tmp_path)
    config.update({"shot_id": "proof", "layout": "fancy_grid", "headline": "X"})
    request = StageRequest(stage="composite.proof", seed=1, config=config)
    with pytest.raises(ValueError):
        asyncio.run(CompositeStage().run(make_context(tmp_path), request))
