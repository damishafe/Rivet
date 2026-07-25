import hashlib
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request

from rivet.adapters.background import BackgroundStage
from rivet.adapters.composite import CompositeStage
from rivet.adapters.motion import MotionStage
from rivet.adapters.narrate import NarrateStage
from rivet.adapters.segment import SegmentStage
from rivet.audit.receipt import build_campaign_receipt
from rivet.audit.semantic import _qwen_judge
from rivet.domain.models import PaletteColor
from rivet.domain.receipt import CampaignReceipt
from rivet.domain.states import ProjectStatus
from rivet.pipeline.runner import JobRunner, PlannedStage
from rivet.pipeline.stage import Stage, StageContext, StageRequest
from rivet.render.assemble import assemble_scenes, mix_narration, write_srt
from rivet.render.pack import build_pack
from rivet.storage.assets import AssetStore
from rivet.storage.jobs import ActiveJobError, JobStore
from rivet.storage.plans import PlanStore
from rivet.storage.projects import ProjectStore
from services.api.deps import get_asset_store, get_plan_store, get_project_store

router = APIRouter(prefix="/api/projects", tags=["campaign"])


def _accent(palette: list[PaletteColor]) -> list[int]:
    if not palette:
        return [255, 59, 0]
    value = palette[0].hex.lstrip("#")
    return [int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16)]


def _sha256(path: str) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _stage(request: Request, name: str, default: Stage) -> Stage:
    resolved = getattr(request.app.state, name, None)
    return resolved if resolved is not None else default


@router.post("/{project_id}/generate/campaign")
async def generate_campaign(
    project_id: str,
    request: Request,
    projects: ProjectStore = Depends(get_project_store),
    plans: PlanStore = Depends(get_plan_store),
    assets: AssetStore = Depends(get_asset_store),
) -> CampaignReceipt:
    project = projects.get(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="project not found")
    if project.status != ProjectStatus.PLANNED:
        raise HTTPException(status_code=409, detail="campaign requires a planned project")
    shots = plans.get_plan(project_id)
    if shots is None:
        raise HTTPException(status_code=409, detail="no storyboard plan")
    brand = projects.get_brand_dna(project_id)
    if brand is None or brand.confirmed_at is None:
        raise HTTPException(status_code=409, detail="confirmed brand dna required")
    product_asset = assets.get(brand.product_asset_id)
    logo_asset = assets.get(brand.logo_asset_id)
    if product_asset is None or logo_asset is None:
        raise HTTPException(status_code=409, detail="confirmed product and logo assets missing")

    engine = request.app.state.engine
    try:
        job = JobStore(engine).create(project_id, "campaign")
    except ActiveJobError as error:
        raise HTTPException(status_code=409, detail="a job is already running") from error
    projects.advance(project_id, ProjectStatus.GENERATING)

    asset_root = request.app.state.asset_root
    workdir = Path(asset_root) / "projects" / project_id / "work" / "campaign"
    cutout_path = str(workdir / "cutout.png")
    logo_path = logo_asset.path
    accent = _accent(brand.palette)

    segment = _stage(request, "segment_stage", SegmentStage())
    background = _stage(request, "background_stage", BackgroundStage())
    composite = CompositeStage()

    plan = [
        PlannedStage(
            stage=segment,
            request=StageRequest(
                stage="segment", seed=project.campaign_seed,
                config={"image_path": product_asset.path},
            ),
        )
    ]
    for shot in shots:
        plan.append(
            PlannedStage(
                stage=background,
                request=StageRequest(
                    stage=f"background.{shot.shot_id}", seed=shot.seed,
                    config={
                        "shot_id": shot.shot_id,
                        "prompt": shot.background_prompt,
                        "negative_prompt": shot.negative_prompt,
                    },
                ),
            )
        )
        plan.append(
            PlannedStage(
                stage=composite,
                request=StageRequest(
                    stage=f"composite.{shot.shot_id}", seed=shot.seed,
                    config={
                        "background_path": str(workdir / f"{shot.shot_id}.png"),
                        "cutout_path": cutout_path,
                        "logo_path": logo_path,
                        "layout": shot.layout_template,
                        "shot_id": shot.shot_id,
                        "headline": shot.copy_.headline,
                        "support": shot.copy_.support,
                        "cta": shot.copy_.cta,
                        "accent": accent,
                    },
                ),
            )
        )

    finished = await JobRunner(engine, asset_root).run(job, plan, workdir=workdir)
    if finished.status != "succeeded":
        projects.advance(project_id, ProjectStatus.FAILED)
        raise HTTPException(status_code=500, detail=f"generation failed: {finished.error}")
    projects.advance(project_id, ProjectStatus.COMPOSED)
    projects.advance(project_id, ProjectStatus.AUDITING)

    backgrounds: dict[str, str] = {
        shot.shot_id: str(workdir / f"{shot.shot_id}.png") for shot in shots
    }
    accent_rgb = (accent[0], accent[1], accent[2])
    judge = getattr(request.app.state, "semantic_judge", _qwen_judge)
    receipt = build_campaign_receipt(
        project_id, shots, workdir, brand, logo_path, cutout_path, backgrounds, accent_rgb,
        judge=judge,
        product_sha_expected=product_asset.sha256, product_sha_used=_sha256(product_asset.path),
        logo_sha_expected=logo_asset.sha256, logo_sha_used=_sha256(logo_asset.path),
    )

    narrate = _stage(request, "narrate_stage", NarrateStage())
    motion = MotionStage()
    context = StageContext(project_id=project_id, job_id=job.id, workdir=workdir)
    clips: list[str] = []
    narration_clips: list[tuple[str, int]] = []
    cues: list[tuple[str, float, float]] = []
    offset = 0.0
    for shot in shots:
        moved = await motion.run(
            context,
            StageRequest(
                stage=f"motion.{shot.shot_id}", seed=shot.seed,
                config={
                    "shot_id": shot.shot_id,
                    "still_path": str(workdir / f"{shot.shot_id}-still.png"),
                    "duration_s": shot.duration_s,
                },
            ),
        )
        clips.append(moved.artifacts["clip"])
        spoken = await narrate.run(
            context,
            StageRequest(
                stage=f"narration.{shot.shot_id}", seed=shot.seed,
                config={"shot_id": shot.shot_id, "text": shot.narration},
            ),
        )
        wav = Path(spoken.artifacts["narration"])
        if wav.exists():
            narration_clips.append((str(wav), int(offset * 1000)))
        cues.append((shot.narration, offset, offset + shot.duration_s))
        offset += shot.duration_s

    silent_path = workdir / "silent.mp4"
    assemble_scenes(clips, silent_path)
    video_path = str(workdir / "campaign.mp4")
    mix_narration(str(silent_path), narration_clips, Path(video_path))
    captions_path = str(workdir / "campaign.srt")
    write_srt(cues, Path(captions_path))

    receipt = receipt.model_copy(
        update={"video_path": video_path, "captions_path": captions_path}
    ).finalize()
    if not receipt.passed:
        projects.advance(project_id, ProjectStatus.NEEDS_REPAIR)
        return receipt

    projects.advance(project_id, ProjectStatus.READY)
    pack_path = str(workdir / "campaign-pack.zip")
    build_pack(workdir, receipt, Path(pack_path))
    projects.advance(project_id, ProjectStatus.EXPORTED)
    return receipt.model_copy(update={"pack_path": pack_path})
