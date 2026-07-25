import argparse
import json
import time
import traceback
from collections.abc import Callable
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from rivet.pipeline.device import resolve_device


@dataclass
class ProbeResult:
    stage: str
    name: str
    device: str
    ok: bool
    load_s: float | None = None
    infer_s: float | None = None
    peak_mb: float | None = None
    note: str = ""
    error: str = ""


@dataclass
class Probe:
    stage: str
    name: str
    run: Callable[[str], ProbeResult]


def _peak_mb(device: str) -> float | None:
    import torch

    if device == "cuda":
        return torch.cuda.max_memory_allocated() / 1e6
    if device == "mps":
        return torch.mps.current_allocated_memory() / 1e6
    return None


def _reset_peak(device: str) -> None:
    import torch

    if device == "cuda":
        torch.cuda.reset_peak_memory_stats()
    elif device == "mps":
        torch.mps.empty_cache()


def _sync(device: str) -> None:
    import torch

    if device == "cuda":
        torch.cuda.synchronize()
    elif device == "mps":
        torch.mps.synchronize()


def probe_whisper(device: str) -> ProbeResult:
    import math

    import numpy as np
    from transformers import WhisperForConditionalGeneration, WhisperProcessor

    name = "openai/whisper-tiny.en"
    _reset_peak(device)
    t0 = time.perf_counter()
    proc = WhisperProcessor.from_pretrained(name)
    model = WhisperForConditionalGeneration.from_pretrained(name).to(device)
    load_s = time.perf_counter() - t0

    sr = 16000
    audio = (0.05 * np.sin(2 * math.pi * 220 * np.arange(sr * 3) / sr)).astype("float32")
    feats = proc(audio, sampling_rate=sr, return_tensors="pt").input_features.to(device)
    t1 = time.perf_counter()
    ids = model.generate(feats, max_new_tokens=16)
    _sync(device)
    infer_s = time.perf_counter() - t1
    text = proc.batch_decode(ids, skip_special_tokens=True)[0]
    return ProbeResult(
        stage="transcription",
        name=name,
        device=device,
        ok=True,
        load_s=round(load_s, 2),
        infer_s=round(infer_s, 2),
        peak_mb=round(_peak_mb(device) or 0, 0),
        note=f"transcript={text.strip()!r}",
    )


def probe_sam2(device: str) -> ProbeResult:
    import numpy as np
    import torch
    from transformers import Sam2Model, Sam2Processor

    name = "facebook/sam2.1-hiera-small"
    _reset_peak(device)
    t0 = time.perf_counter()
    proc = Sam2Processor.from_pretrained(name)
    model = Sam2Model.from_pretrained(name).to(device)
    load_s = time.perf_counter() - t0

    img = np.zeros((256, 256, 3), dtype="uint8")
    img[64:192, 64:192] = 200
    inputs = proc(
        images=img, input_points=[[[[128, 128]]]], input_labels=[[[1]]], return_tensors="pt"
    ).to(device)
    t1 = time.perf_counter()
    with torch.no_grad():
        out = model(**inputs)
    _sync(device)
    infer_s = time.perf_counter() - t1
    return ProbeResult(
        stage="segmentation",
        name=name,
        device=device,
        ok=True,
        load_s=round(load_s, 2),
        infer_s=round(infer_s, 2),
        peak_mb=round(_peak_mb(device) or 0, 0),
        note=f"masks={tuple(out.pred_masks.shape)}",
    )


def probe_kokoro(device: str) -> ProbeResult:
    from kokoro import KPipeline

    name = "hexgrad/Kokoro-82M"
    _reset_peak(device)
    t0 = time.perf_counter()
    pipe = KPipeline(lang_code="a", device=device)
    load_s = time.perf_counter() - t0

    text = "Make every space your studio."
    t1 = time.perf_counter()
    chunks = list(pipe(text, voice="af_heart"))
    _sync(device)
    infer_s = time.perf_counter() - t1
    secs = len(chunks[0].audio) / 24000
    return ProbeResult(
        stage="narration",
        name=name,
        device=device,
        ok=True,
        load_s=round(load_s, 2),
        infer_s=round(infer_s, 2),
        peak_mb=round(_peak_mb(device) or 0, 0),
        note=f"{secs:.1f}s speech",
    )


def probe_sdxl(device: str) -> ProbeResult:
    import numpy as np
    import torch
    from diffusers import AutoencoderKL, StableDiffusionXLPipeline

    name = "stabilityai/stable-diffusion-xl-base-1.0"
    _reset_peak(device)
    t0 = time.perf_counter()
    vae = AutoencoderKL.from_pretrained("madebyollin/sdxl-vae-fp16-fix", torch_dtype=torch.float16)
    pipe = StableDiffusionXLPipeline.from_pretrained(
        name, vae=vae, torch_dtype=torch.float16, variant="fp16", use_safetensors=True
    ).to(device)
    load_s = time.perf_counter() - t0

    prompt = "bold energetic studio backdrop, orange and charcoal, soft gradient, no product, no text"
    t1 = time.perf_counter()
    image = pipe(
        prompt=prompt, height=1216, width=832, num_inference_steps=8, guidance_scale=6.0
    ).images[0]
    _sync(device)
    infer_s = time.perf_counter() - t1
    real = float(np.asarray(image).std()) > 5.0
    return ProbeResult(
        stage="background",
        name=name,
        device=device,
        ok=real,
        load_s=round(load_s, 1),
        infer_s=round(infer_s, 1),
        peak_mb=round(_peak_mb(device) or 0, 0),
        note=f"plate {image.size} 8 steps" if real else "black/nan output",
        error="" if real else "fp16 vae produced a black image",
    )


PROBES: tuple[Probe, ...] = (
    Probe("transcription", "whisper-tiny.en", probe_whisper),
    Probe("segmentation", "sam2.1-hiera-small", probe_sam2),
    Probe("narration", "kokoro-82M", probe_kokoro),
    Probe("background", "sdxl-base-1.0", probe_sdxl),
)


def run(selected: set[str] | None) -> list[ProbeResult]:
    device = resolve_device()
    results: list[ProbeResult] = []
    for probe in PROBES:
        if selected is not None and probe.name not in selected:
            continue
        try:
            results.append(probe.run(device))
        except Exception as error:  # noqa: BLE001
            results.append(
                ProbeResult(
                    stage=probe.stage,
                    name=probe.name,
                    device=device,
                    ok=False,
                    error=f"{type(error).__name__}: {error}",
                    note=traceback.format_exc().splitlines()[-1],
                )
            )
    return results


def render_markdown(results: list[ProbeResult]) -> str:
    header = "| stage | model | device | ok | load s | infer s | peak MB | note |"
    sep = "|---|---|---|---|---|---|---|---|"
    rows = [header, sep]
    for r in results:
        mark = "PASS" if r.ok else "FAIL"
        detail = r.note if r.ok else r.error
        rows.append(
            f"| {r.stage} | {r.name} | {r.device} | {mark} | "
            f"{r.load_s or ''} | {r.infer_s or ''} | {r.peak_mb or ''} | {detail} |"
        )
    return "\n".join(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="Rivet model smoke-test matrix")
    parser.add_argument("--only", nargs="*", help="probe names to run (default: all)")
    parser.add_argument("--out", type=Path, help="write JSON results to this path")
    args = parser.parse_args()

    selected = set(args.only) if args.only else None
    results = run(selected)
    table = render_markdown(results)
    print(table)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        payload: dict[str, Any] = {"results": [asdict(r) for r in results]}
        args.out.write_text(json.dumps(payload, indent=2))
    return 0 if all(r.ok for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
