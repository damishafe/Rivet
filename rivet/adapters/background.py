from collections.abc import Callable
from pathlib import Path
from typing import Any

from rivet.adapters.model_cache import resolve_model
from rivet.pipeline.device import resolve_device
from rivet.pipeline.fingerprint import cache_key
from rivet.pipeline.stage import (
    ModelManifest,
    ResourcePlan,
    StageContext,
    StageRequest,
    StageResult,
)

BackgroundGenerator = Callable[[dict[str, Any], int, str, Path], None]

DEFAULT_WIDTH = 832
DEFAULT_HEIGHT = 1216
DEFAULT_STEPS = 8
DEFAULT_GUIDANCE = 6.0


def _sdxl_generate(config: dict[str, Any], seed: int, device: str, out_path: Path) -> None:
    import torch
    from diffusers import AutoencoderKL, StableDiffusionXLPipeline

    vae = AutoencoderKL.from_pretrained(
        resolve_model("madebyollin/sdxl-vae-fp16-fix"), torch_dtype=torch.float16
    )
    pipe = StableDiffusionXLPipeline.from_pretrained(
        resolve_model("stabilityai/stable-diffusion-xl-base-1.0"),
        vae=vae,
        torch_dtype=torch.float16,
        variant="fp16",
        use_safetensors=True,
    ).to(device)
    generator = torch.Generator(device="cpu").manual_seed(seed)
    image = pipe(
        prompt=config["prompt"],
        negative_prompt=config.get("negative_prompt", ""),
        height=int(config.get("height", DEFAULT_HEIGHT)),
        width=int(config.get("width", DEFAULT_WIDTH)),
        num_inference_steps=int(config.get("steps", DEFAULT_STEPS)),
        guidance_scale=float(config.get("guidance", DEFAULT_GUIDANCE)),
        generator=generator,
    ).images[0]
    image.save(out_path)


class BackgroundStage:
    name = "background"
    version = "1"

    def __init__(self, generator: BackgroundGenerator | None = None) -> None:
        self._generator = generator or _sdxl_generate

    def fingerprint(self, request: StageRequest, manifest: ModelManifest | None) -> str:
        return cache_key(self.name, self.version, request, manifest)

    def estimate_resources(self, request: StageRequest) -> ResourcePlan:
        return ResourcePlan(est_vram_mb=8000, prefers_gpu=True)

    async def run(self, context: StageContext, request: StageRequest) -> StageResult:
        config = request.config
        shot_id = str(config["shot_id"])
        out = context.workdir / f"{shot_id}.png"
        self._generator(config, request.seed, resolve_device(), out)
        return StageResult(
            artifacts={"plate": str(out)},
            metrics={
                "width": float(config.get("width", DEFAULT_WIDTH)),
                "height": float(config.get("height", DEFAULT_HEIGHT)),
            },
        )

    async def cleanup(self) -> None:
        return None
