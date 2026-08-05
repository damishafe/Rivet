from collections.abc import Callable
from pathlib import Path

from rivet.adapters import residency
from rivet.domain.languages import Language, language
from rivet.pipeline.device import resolve_device
from rivet.pipeline.fingerprint import cache_key
from rivet.pipeline.stage import (
    ModelManifest,
    ResourcePlan,
    StageContext,
    StageRequest,
    StageResult,
)

Narrator = Callable[[str, str, Path, Language], float]
SAMPLE_RATE = 24000


def _kokoro_narrate(text: str, device: str, out_path: Path, lang: Language) -> float:
    import numpy as np
    import soundfile as sf

    def load() -> object:
        from kokoro import KPipeline

        return KPipeline(lang_code=lang.kokoro_code, device=device)

    pipe = residency.acquire(f"kokoro:{device}:{lang.code}", load)
    chunks = [chunk.audio for chunk in pipe(text, voice=lang.voice)]
    audio = np.concatenate(chunks) if chunks else np.zeros(1, dtype="float32")
    sf.write(out_path, audio, SAMPLE_RATE)
    return float(len(audio) / SAMPLE_RATE)


class NarrateStage:
    name = "narration"
    version = "1"

    def __init__(self, narrator: Narrator | None = None) -> None:
        self._narrator = narrator or _kokoro_narrate

    def fingerprint(self, request: StageRequest, manifest: ModelManifest | None) -> str:
        return cache_key(self.name, self.version, request, manifest)

    def estimate_resources(self, request: StageRequest) -> ResourcePlan:
        return ResourcePlan(est_vram_mb=1000, prefers_gpu=False)

    async def run(self, context: StageContext, request: StageRequest) -> StageResult:
        config = request.config
        shot_id = str(config["shot_id"])
        text = str(config.get("text", ""))
        out = context.workdir / f"{shot_id}-narration.wav"
        lang = language(config.get("language"))
        duration = self._narrator(text, resolve_device(), out, lang) if text else 0.0
        return StageResult(artifacts={"narration": str(out)}, metrics={"duration_s": duration})

    async def cleanup(self) -> None:
        return None
