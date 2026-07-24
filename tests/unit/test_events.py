import pytest
from pydantic import ValidationError

from rivet.domain.events import GpuSample, StageEvent


def test_event_serializes_to_contract_shape() -> None:
    event = StageEvent(
        job_id="j1",
        project_id="p1",
        stage="background.generate",
        shot_id="hook",
        status="running",
        progress=0.42,
        elapsed_ms=18420,
        gpu=GpuSample(vram_used_mb=21480, utilization_pct=96),
        message="Denoising step 12 of 28",
    )
    payload = event.model_dump(mode="json")
    assert payload["stage"] == "background.generate"
    assert payload["gpu"] == {"vram_used_mb": 21480, "utilization_pct": 96}
    assert StageEvent.model_validate(payload) == event


def test_progress_bounded() -> None:
    with pytest.raises(ValidationError):
        StageEvent(job_id="j", project_id="p", stage="s", status="running", progress=1.5)


def test_gpu_is_optional() -> None:
    event = StageEvent(job_id="j", project_id="p", stage="s", status="queued", progress=0)
    assert event.gpu is None
    assert event.shot_id is None
