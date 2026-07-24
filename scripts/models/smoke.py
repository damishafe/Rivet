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


PROBES: tuple[Probe, ...] = (Probe("transcription", "whisper-tiny.en", probe_whisper),)


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
