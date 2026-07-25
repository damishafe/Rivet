from pathlib import Path

from fastapi import APIRouter, HTTPException, Request

from rivet.domain.receipt import CampaignReceipt
from rivet.pipeline.campaign import run_campaign
from rivet.pipeline.campaign_inputs import (
    CampaignConflict,
    CampaignFailed,
    CampaignNotFound,
    CampaignStages,
)

router = APIRouter(prefix="/api/projects", tags=["campaign"])

_STAGE_OVERRIDES = ("segment", "background", "narrate")


def _stages(request: Request) -> CampaignStages:
    stages = CampaignStages()
    for name in _STAGE_OVERRIDES:
        override = getattr(request.app.state, f"{name}_stage", None)
        if override is not None:
            setattr(stages, name, override)
    return stages


@router.post("/{project_id}/generate/campaign")
async def generate_campaign(project_id: str, request: Request) -> CampaignReceipt:
    try:
        return await run_campaign(
            request.app.state.engine,
            Path(request.app.state.asset_root),
            project_id,
            _stages(request),
            getattr(request.app.state, "semantic_judge", None),
        )
    except CampaignNotFound as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except CampaignConflict as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    except CampaignFailed as error:
        raise HTTPException(status_code=500, detail=str(error)) from error
