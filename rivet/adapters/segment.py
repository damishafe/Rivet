from collections.abc import Callable
from pathlib import Path
from typing import Any

from PIL import Image

from rivet.adapters.cutout import deterministic_alpha, write_cutout
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

Segmenter = Callable[[str, dict[str, Any], str, Path], float]


def _sam_segment(image_path: str, config: dict[str, Any], device: str, out_path: Path) -> float:
    import numpy as np
    import torch
    from PIL import Image
    from transformers import Sam2Model, Sam2Processor

    name = resolve_model("facebook/sam2.1-hiera-small")
    proc = Sam2Processor.from_pretrained(name)
    model = Sam2Model.from_pretrained(name).to(device)
    image = Image.open(image_path).convert("RGB")
    width, height = image.size
    points = config.get("points") or [[[[width // 2, height // 2]]]]
    labels = config.get("labels") or [[[1]]]
    inputs = proc(
        images=image, input_points=points, input_labels=labels, return_tensors="pt"
    ).to(device)
    with torch.no_grad():
        out = model(**inputs)
    masks = proc.post_process_masks(out.pred_masks.cpu(), inputs["original_sizes"])[0]
    scores = out.iou_scores.cpu().numpy().reshape(-1)
    best = int(scores.argmax())
    mask = np.asarray(masks).reshape(-1, height, width)[best] > 0.5
    rgba = np.dstack([np.asarray(image), (mask * 255).astype("uint8")])
    Image.fromarray(rgba, "RGBA").save(out_path)
    return float(scores[best])


def _default_segment(image_path: str, config: dict[str, Any], device: str, out_path: Path) -> float:
    with Image.open(image_path) as source:
        image = source.copy()
    alpha = deterministic_alpha(image)
    if alpha is not None:
        write_cutout(image, alpha, str(out_path))
        return 1.0
    return _sam_segment(image_path, config, device, out_path)


class SegmentStage:
    name = "segmentation"
    version = "2"

    def __init__(self, segmenter: Segmenter | None = None) -> None:
        self._segmenter = segmenter or _default_segment

    def fingerprint(self, request: StageRequest, manifest: ModelManifest | None) -> str:
        return cache_key(self.name, self.version, request, manifest)

    def estimate_resources(self, request: StageRequest) -> ResourcePlan:
        return ResourcePlan(est_vram_mb=2000, prefers_gpu=True)

    async def run(self, context: StageContext, request: StageRequest) -> StageResult:
        image_path = str(request.config["image_path"])
        out = context.workdir / "cutout.png"
        confidence = self._segmenter(image_path, request.config, resolve_device(), out)
        return StageResult(
            artifacts={"cutout": str(out)},
            metrics={"confidence": confidence},
        )

    async def cleanup(self) -> None:
        return None
