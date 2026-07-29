from pathlib import Path

from sqlalchemy.engine import Engine

from rivet.adapters import residency
from rivet.audit.receipt import build_campaign_receipt
from rivet.audit.semantic import SemanticJudge, qwen_judge
from rivet.domain.receipt import CampaignReceipt
from rivet.domain.states import ProjectStatus
from rivet.pipeline.campaign_inputs import (
    CampaignConflict,
    CampaignFailed,
    CampaignInputs,
    CampaignStages,
    accent_rgb,
    generation_plan,
    render_plan,
    resolve_campaign_inputs,
    sha256_file,
)
from rivet.pipeline.runner import JobRunner
from rivet.render.assemble import assemble_scenes, mix_narration, write_srt
from rivet.render.pack import build_pack
from rivet.storage.jobs import ActiveJobError, JobStore
from rivet.storage.projects import ProjectStore


def _assemble_campaign(inputs: CampaignInputs, workdir: Path) -> tuple[str, str]:
    clips: list[str] = []
    narration_clips: list[tuple[str, int]] = []
    cues: list[tuple[str, float, float]] = []
    offset = 0.0
    for shot in inputs.shots:
        clips.append(str(workdir / f"{shot.shot_id}.mp4"))
        wav = workdir / f"{shot.shot_id}-narration.wav"
        if wav.exists():
            narration_clips.append((str(wav), int(offset * 1000)))
        cues.append((shot.narration, offset, offset + shot.duration_s))
        offset += shot.duration_s

    silent_path = workdir / "silent.mp4"
    assemble_scenes(clips, silent_path)
    video_path = str(workdir / "campaign.mp4")
    mix_narration(str(silent_path), narration_clips, Path(video_path), duration_s=offset)
    captions_path = str(workdir / "campaign.srt")
    write_srt(cues, Path(captions_path))
    return video_path, captions_path


async def run_campaign(
    engine: Engine,
    asset_root: Path,
    project_id: str,
    stages: CampaignStages | None = None,
    judge: SemanticJudge | None = None,
    semantic: bool = True,
) -> CampaignReceipt:
    inputs = resolve_campaign_inputs(engine, asset_root, project_id)
    stages = stages if stages is not None else CampaignStages()
    projects = ProjectStore(engine)
    try:
        job = JobStore(engine).create(project_id, "campaign")
    except ActiveJobError as error:
        raise CampaignConflict("a job is already running") from error
    projects.advance(project_id, ProjectStatus.GENERATING)

    workdir = Path(asset_root) / "projects" / project_id / "work" / "campaign"
    cutout_path = str(workdir / "cutout.png")
    accent = accent_rgb(inputs.brand.palette)

    runner = JobRunner(engine, asset_root)
    jobs = JobStore(engine)
    jobs.set_status(job.id, "running")
    generation = await runner.run_phase(
        job, generation_plan(inputs, stages, workdir, accent), workdir
    )
    if generation.status != "succeeded":
        jobs.set_status(job.id, generation.status, error=generation.error)
        projects.advance(project_id, ProjectStatus.FAILED)
        raise CampaignFailed(f"generation failed: {generation.error}")
    projects.advance(project_id, ProjectStatus.COMPOSED)
    projects.advance(project_id, ProjectStatus.AUDITING)

    try:
        backgrounds: dict[str, str] = {
            shot.shot_id: str(workdir / f"{shot.shot_id}.png") for shot in inputs.shots
        }
        receipt = build_campaign_receipt(
            project_id, inputs.shots, workdir, inputs.brand, inputs.logo.path, cutout_path,
            backgrounds, accent,
            judge=(judge if judge is not None else qwen_judge) if semantic else None,
            product_sha_expected=inputs.product.sha256,
            product_sha_used=sha256_file(inputs.product.path),
            logo_sha_expected=inputs.logo.sha256,
            logo_sha_used=sha256_file(inputs.logo.path),
        )
        render = await runner.run_phase(job, render_plan(inputs, stages, workdir), workdir)
        if render.status != "succeeded":
            raise CampaignFailed(f"render failed: {render.error}")
        video_path, captions_path = _assemble_campaign(inputs, workdir)
        receipt = receipt.model_copy(
            update={"video_path": video_path, "captions_path": captions_path}
        ).finalize()
        (workdir / "receipt.json").write_text(receipt.model_dump_json(indent=2))
        if not receipt.passed:
            projects.advance(project_id, ProjectStatus.NEEDS_REPAIR)
            return receipt
        pack_path = str(workdir / "campaign-pack.zip")
        build_pack(workdir, receipt, Path(pack_path))
    except Exception as error:
        jobs.set_status(job.id, "failed", error=str(error))
        projects.advance(project_id, ProjectStatus.FAILED)
        raise CampaignFailed(f"campaign failed after generation: {error}") from error
    finally:
        residency.release_all()
    jobs.set_status(job.id, "succeeded")
    projects.advance(project_id, ProjectStatus.READY)
    projects.advance(project_id, ProjectStatus.EXPORTED)
    return receipt.model_copy(update={"pack_path": pack_path})
