import asyncio
from pathlib import Path

import numpy as np
import soundfile as sf

from rivet.adapters.narrate import NarrateStage
from rivet.pipeline.stage import StageContext, StageRequest


def make_context(tmp_path: Path) -> StageContext:
    workdir = tmp_path / "work"
    workdir.mkdir()
    return StageContext(project_id="p1", job_id="j1", workdir=workdir)


def fake_narrator(text: str, device: str, out_path: Path) -> float:
    sf.write(out_path, np.zeros(24000, dtype="float32"), 24000)
    return 1.0


def test_narrate_writes_wav(tmp_path: Path) -> None:
    stage = NarrateStage(narrator=fake_narrator)
    request = StageRequest(stage="narration.hook", seed=1, config={"shot_id": "hook", "text": "Kora Arc"})
    result = asyncio.run(stage.run(make_context(tmp_path), request))
    wav = Path(result.artifacts["narration"])
    assert wav.name == "hook-narration.wav"
    assert wav.exists()
    assert result.metrics["duration_s"] == 1.0


def test_empty_text_skips_narrator(tmp_path: Path) -> None:
    calls: list[str] = []

    def spy(text: str, device: str, out_path: Path) -> float:
        calls.append(text)
        return 2.0

    stage = NarrateStage(narrator=spy)
    request = StageRequest(stage="narration.hook", seed=1, config={"shot_id": "hook", "text": ""})
    result = asyncio.run(stage.run(make_context(tmp_path), request))
    assert result.metrics["duration_s"] == 0.0
    assert calls == []
