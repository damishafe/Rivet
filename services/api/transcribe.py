from fastapi import APIRouter, Depends, HTTPException, Request

from rivet.adapters.transcribe import TranscribeStage
from rivet.domain.jobs import Job
from rivet.pipeline.runner import JobRunner, PlannedStage
from rivet.pipeline.stage import StageRequest
from rivet.storage.assets import AssetStore
from rivet.storage.jobs import ActiveJobError, JobStore
from rivet.storage.projects import ProjectStore
from services.api.deps import get_asset_store, get_project_store

router = APIRouter(prefix="/api/projects", tags=["transcribe"])


@router.post("/{project_id}/transcribe", status_code=202)
async def transcribe(
    project_id: str,
    request: Request,
    projects: ProjectStore = Depends(get_project_store),
    assets: AssetStore = Depends(get_asset_store),
) -> Job:
    project = projects.get(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="project not found")
    clips = assets.find(project_id, "brief_audio")
    if not clips:
        raise HTTPException(status_code=409, detail="no voice brief uploaded")
    engine = request.app.state.engine
    try:
        job = JobStore(engine).create(project_id, "transcribe")
    except ActiveJobError as error:
        raise HTTPException(status_code=409, detail="a job is already running") from error
    stage = getattr(request.app.state, "transcribe_stage", None) or TranscribeStage()
    plan = [
        PlannedStage(
            stage=stage,
            request=StageRequest(
                stage="transcription",
                seed=project.campaign_seed,
                config={"audio_path": clips[-1].path},
                input_hashes=[clips[-1].sha256],
            ),
        )
    ]
    return await JobRunner(engine, request.app.state.asset_root).run(job, plan)
