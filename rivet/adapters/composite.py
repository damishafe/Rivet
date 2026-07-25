from PIL import Image

from rivet.compositor.compose import compose_still
from rivet.domain.layouts import LayoutTemplate, is_layout
from rivet.pipeline.fingerprint import cache_key
from rivet.pipeline.stage import (
    ModelManifest,
    ResourcePlan,
    StageContext,
    StageRequest,
    StageResult,
)


class CompositeStage:
    name = "composite"
    version = "1"

    def fingerprint(self, request: StageRequest, manifest: ModelManifest | None) -> str:
        return cache_key(self.name, self.version, request, manifest)

    def estimate_resources(self, request: StageRequest) -> ResourcePlan:
        return ResourcePlan(est_vram_mb=0, prefers_gpu=False)

    async def run(self, context: StageContext, request: StageRequest) -> StageResult:
        config = request.config
        background = Image.open(config["background_path"]).convert("RGB")
        cutout = Image.open(config["cutout_path"]).convert("RGBA")
        logo = Image.open(config["logo_path"]).convert("RGBA")
        raw_layout = str(config["layout"])
        layout: LayoutTemplate = raw_layout if is_layout(raw_layout) else "center_hero"
        raw = config.get("accent", [255, 59, 0])
        accent = (int(raw[0]), int(raw[1]), int(raw[2]))
        still = compose_still(
            background,
            cutout,
            logo,
            str(config.get("headline", "")),
            str(config.get("support", "")),
            str(config.get("cta", "")),
            layout,
            accent,
        )
        out = context.workdir / f"{config['shot_id']}-still.png"
        still.save(out)
        return StageResult(
            artifacts={"still": str(out)},
            metrics={"width": float(still.width), "height": float(still.height)},
        )

    async def cleanup(self) -> None:
        return None
