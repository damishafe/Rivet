"""Download every model Rivet uses, pinned to the revisions in MODEL_LICENSES.md.

Only the weights the pipeline actually loads are fetched: SDXL ships fp32, fp16 and
single-file checkpoints of the same network, and Rivet loads the fp16 variant, so the
rest is skipped. On a metered GPU instance that is the difference between minutes and
tens of minutes.
"""

import argparse
import sys
import time
from dataclasses import dataclass, field

WEIGHT_NOISE = ["*.bin", "*.ckpt", "*.msgpack", "*.onnx", "*openvino*", "*.h5"]
VOICES = ("af_heart", "ef_dora", "ff_siwis", "if_sara", "pf_dora", "zf_xiaobei")


@dataclass
class Model:
    repo_id: str
    revision: str
    purpose: str
    ignore: list[str] = field(default_factory=list)
    require: list[str] = field(default_factory=list)


MODELS = (
    Model(
        repo_id="stabilityai/stable-diffusion-xl-base-1.0",
        revision="462165984030d82259a11f4367a4eed129e94a7b",
        purpose="scene backgrounds",
        ignore=[
            *WEIGHT_NOISE,
            "sd_xl_base_1.0.safetensors",
            "sd_xl_base_1.0_0.9vae.safetensors",
            "diffusion_pytorch_model.safetensors",
            "model.safetensors",
        ],
    ),
    Model(
        repo_id="madebyollin/sdxl-vae-fp16-fix",
        revision="207b116dae70ace3637169f1ddd2434b91b3a8cd",
        purpose="fp16-safe VAE",
        # The whole repo is the fp16 fix: diffusion_pytorch_model.safetensors IS the
        # model here, not a duplicate of an fp16 variant. Excluding it leaves a config
        # with no weights, which only fails at load time.
        ignore=WEIGHT_NOISE,
    ),
    Model(
        repo_id="Qwen/Qwen3-VL-4B-Instruct",
        revision="ebb281ec70b05090aa6165b016eac8ec08e71b17",
        purpose="scene planning and the advisory A08 audit",
        ignore=WEIGHT_NOISE,
    ),
    Model(
        repo_id="facebook/sam2.1-hiera-small",
        revision="ee5bba1d82bb8749febdf90f45e84b687142ba03",
        purpose="product cutout",
        ignore=WEIGHT_NOISE,
    ),
    Model(
        repo_id="hexgrad/Kokoro-82M",
        revision="f3ff3571791e39611d31c381e3a41a3af07b4987",
        purpose="narration in every supported language",
        ignore=["*.onnx", "*openvino*"],
        require=[f"voices/{voice}.pt" for voice in VOICES],
    ),
    Model(
        repo_id="openai/whisper-tiny.en",
        revision="87c7102498dcde7456f24cfd30239ca606ed9063",
        purpose="brief transcription",
        ignore=WEIGHT_NOISE,
    ),
)


WEIGHT_SUFFIXES = frozenset({".safetensors", ".bin", ".pth", ".pt", ".gguf"})


def _cached(model: Model) -> bool:
    from rivet.adapters.model_cache import local_snapshot

    snapshot = local_snapshot(model.repo_id)
    if snapshot is None or snapshot.name != model.revision:
        return False
    # A snapshot holding only config files reports as present and fails at load
    # time instead, which on metered hardware is discovered expensively.
    if not any(path.suffix in WEIGHT_SUFFIXES for path in snapshot.rglob("*")):
        return False
    # Narration voices live in their own files: the model can be complete while the
    # voice a language needs is absent, which only surfaces mid-generation.
    return all((snapshot / name).exists() for name in model.require)


def fetch(model: Model) -> float:
    from huggingface_hub import snapshot_download

    started = time.perf_counter()
    snapshot_download(
        repo_id=model.repo_id,
        revision=model.revision,
        ignore_patterns=model.ignore or None,
    )
    return time.perf_counter() - started


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="report cache state and exit")
    args = parser.parse_args()

    missing = [model for model in MODELS if not _cached(model)]
    for model in MODELS:
        state = "cached" if model not in missing else "MISSING"
        print(f"  [{state:>7}] {model.repo_id}@{model.revision[:12]} — {model.purpose}")
    if args.check:
        return 0 if not missing else 1
    if not missing:
        print("all models present at the pinned revisions")
        return 0

    total = 0.0
    for model in missing:
        print(f"fetching {model.repo_id} ...", flush=True)
        elapsed = fetch(model)
        total += elapsed
        print(f"  done in {elapsed:.0f}s")
    print(f"downloaded {len(missing)} model(s) in {total / 60:.1f} min")
    return 0


if __name__ == "__main__":
    sys.exit(main())
