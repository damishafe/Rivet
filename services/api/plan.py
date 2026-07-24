from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from rivet.adapters.heuristic_planner import propose_shots
from rivet.domain.models import PlanValidationError, ShotPlan
from rivet.storage.plans import PlanStore
from rivet.storage.projects import ProjectStore
from services.api.deps import get_plan_store, get_project_store

router = APIRouter(prefix="/api/projects", tags=["plan"])


class PlanResponse(BaseModel):
    shots: list[ShotPlan]


@router.post("/{project_id}/plan")
def derive_plan(
    project_id: str,
    projects: ProjectStore = Depends(get_project_store),
    plans: PlanStore = Depends(get_plan_store),
) -> PlanResponse:
    project = projects.get(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="project not found")
    dna = projects.get_brand_dna(project_id)
    if dna is None or dna.confirmed_at is None:
        raise HTTPException(status_code=409, detail="confirmed brand dna required")
    shots = propose_shots(dna, project.campaign_seed)
    plans.set_plan(project_id, shots)
    return PlanResponse(shots=shots)


@router.put("/{project_id}/shots/{shot_id}")
def edit_shot(
    project_id: str,
    shot_id: str,
    shot: ShotPlan,
    projects: ProjectStore = Depends(get_project_store),
    plans: PlanStore = Depends(get_plan_store),
) -> PlanResponse:
    if projects.get(project_id) is None:
        raise HTTPException(status_code=404, detail="project not found")
    if shot.shot_id != shot_id:
        raise HTTPException(status_code=422, detail="shot id mismatch")
    try:
        shots = plans.update_shot(project_id, shot)
    except LookupError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    except PlanValidationError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    return PlanResponse(shots=shots)


@router.get("/{project_id}/plan")
def get_plan(
    project_id: str,
    projects: ProjectStore = Depends(get_project_store),
    plans: PlanStore = Depends(get_plan_store),
) -> PlanResponse:
    if projects.get(project_id) is None:
        raise HTTPException(status_code=404, detail="project not found")
    shots = plans.get_plan(project_id)
    if shots is None:
        raise HTTPException(status_code=404, detail="plan not set")
    return PlanResponse(shots=shots)
