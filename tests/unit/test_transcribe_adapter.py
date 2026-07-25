import asyncio
from pathlib import Path

from rivet.adapters.transcribe import TranscribeStage
from rivet.pipeline.stage import ModelManifest, StageContext, StageRequest


def make_context(tmp_path: Path) -> StageContext:
    workdir = tmp_path / "work"
    workdir.mkdir()
    return StageContext(project_id="p1", job_id="j1", workdir=workdir)


def test_writes_transcript_artifact(tmp_path: Path) -> None:
    audio = tmp_path / "brief.wav"
    audio.write_bytes(b"fake")
    stage = TranscribeStage(transcriber=lambda path, device: "hello campus creators")
    request = StageRequest(stage="transcription", seed=1, config={"audio_path": str(audio)})
    result = asyncio.run(stage.run(make_context(tmp_path), request))
    transcript = Path(result.artifacts["transcript"])
    assert transcript.read_text() == "hello campus creators"
    assert result.metrics["chars"] == 21.0


def test_fingerprint_is_stable(tmp_path: Path) -> None:
    stage = TranscribeStage(transcriber=lambda path, device: "x")
    request = StageRequest(stage="transcription", seed=1, config={"audio_path": "/a.wav"})
    manifest = ModelManifest(repo="openai/whisper", revision="r1", dtype="fp16")
    assert stage.fingerprint(request, manifest) == stage.fingerprint(request, manifest)


def test_estimate_resources_is_light() -> None:
    plan = TranscribeStage(transcriber=lambda path, device: "x").estimate_resources(
        StageRequest(stage="transcription", seed=1)
    )
    assert plan.est_vram_mb <= 8000
