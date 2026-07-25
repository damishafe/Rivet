from rivet.pipeline.fingerprint import cache_key
from rivet.pipeline.stage import (
    ModelManifest,
    ResourcePlan,
    StageContext,
    StageRequest,
    StageResult,
)
from rivet.render.motion import animate_still

_MOTION_BY_SHOT = {"hook": "zoom_in", "proof": "pan_up", "cta": "zoom_in"}


class MotionStage:
    name = "motion"
    version = "1"

    def fingerprint(self, request: StageRequest, manifest: ModelManifest | None) -> str:
        return cache_key(self.name, self.version, request, manifest)

    def estimate_resources(self, request: StageRequest) -> ResourcePlan:
        return ResourcePlan(est_vram_mb=0, prefers_gpu=False)

    async def run(self, context: StageContext, request: StageRequest) -> StageResult:
        config = request.config
        shot_id = str(config["shot_id"])
        still_path = str(config["still_path"])
        duration = float(config.get("duration_s", 4.0))
        motion = str(config.get("motion", _MOTION_BY_SHOT.get(shot_id, "zoom_in")))
        out = context.workdir / f"{shot_id}.mp4"
        animate_still(still_path, out, duration, motion)
        return StageResult(artifacts={"clip": str(out)}, metrics={"duration_s": duration})

    async def cleanup(self) -> None:
        return None
