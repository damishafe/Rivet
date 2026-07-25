from collections.abc import Callable

from rivet.pipeline.device import resolve_device
from rivet.pipeline.fingerprint import cache_key
from rivet.pipeline.stage import (
    ModelManifest,
    ResourcePlan,
    StageContext,
    StageRequest,
    StageResult,
)

Transcriber = Callable[[str, str], str]


def _whisper_transcribe(audio_path: str, device: str) -> str:
    import soundfile as sf
    from transformers import WhisperForConditionalGeneration, WhisperProcessor

    name = "openai/whisper-large-v3-turbo"
    proc = WhisperProcessor.from_pretrained(name)
    model = WhisperForConditionalGeneration.from_pretrained(name).to(device)
    audio, sr = sf.read(audio_path, dtype="float32")
    if audio.ndim > 1:
        audio = audio.mean(axis=1)
    feats = proc(audio, sampling_rate=sr, return_tensors="pt").input_features.to(device)
    ids = model.generate(feats, max_new_tokens=256)
    return str(proc.batch_decode(ids, skip_special_tokens=True)[0]).strip()


class TranscribeStage:
    name = "transcription"
    version = "1"

    def __init__(self, transcriber: Transcriber | None = None) -> None:
        self._transcriber = transcriber or _whisper_transcribe

    def fingerprint(self, request: StageRequest, manifest: ModelManifest | None) -> str:
        return cache_key(self.name, self.version, request, manifest)

    def estimate_resources(self, request: StageRequest) -> ResourcePlan:
        return ResourcePlan(est_vram_mb=4000, prefers_gpu=True)

    async def run(self, context: StageContext, request: StageRequest) -> StageResult:
        audio_path = str(request.config["audio_path"])
        text = self._transcriber(audio_path, resolve_device())
        out = context.workdir / "transcript.txt"
        out.write_text(text)
        return StageResult(
            artifacts={"transcript": str(out)},
            metrics={"chars": float(len(text))},
        )

    async def cleanup(self) -> None:
        return None
