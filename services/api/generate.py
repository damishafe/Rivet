from fastapi import APIRouter, Depends, HTTPException, Request

from rivet.adapters.background import BackgroundStage
from rivet.domain.jobs import Job
from rivet.pipeline.runner import JobRunner, PlannedStage
from rivet.pipeline.stage import StageRequest
from rivet.storage.jobs import ActiveJobError, JobStore
from rivet.storage.plans import PlanStore
from rivet.storage.projects import ProjectStore
from services.api.deps import get_plan_store, get_project_store

router = APIRouter(prefix="/api/projects", tags=["generate"])


@router.post("/{project_id}/generate/backgrounds", status_code=202)
async def generate_backgrounds(
    project_id: str,
    request: Request,
    projects: ProjectStore = Depends(get_project_store),
    plans: PlanStore = Depends(get_plan_store),
) -> Job:
    project = projects.get(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="project not found")
    shots = plans.get_plan(project_id)
    if shots is None:
        raise HTTPException(status_code=409, detail="no storyboard plan")
    engine = request.app.state.engine
    try:
        job = JobStore(engine).create(project_id, "backgrounds")
    except ActiveJobError as error:
        raise HTTPException(status_code=409, detail="a job is already running") from error
    stage = getattr(request.app.state, "background_stage", None) or BackgroundStage()
    plan = [
        PlannedStage(
            stage=stage,
            request=StageRequest(
                stage=f"background.{shot.shot_id}",
                seed=shot.seed,
                config={
                    "shot_id": shot.shot_id,
                    "prompt": shot.background_prompt,
                    "negative_prompt": shot.negative_prompt,
                },
            ),
        )
        for shot in shots
    ]
    return await JobRunner(engine, request.app.state.asset_root).run(job, plan)
