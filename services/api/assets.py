from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from rivet.domain.media import (
    InvalidMedia,
    MediaTooLarge,
    UnsupportedMediaType,
    validate_upload,
)
from rivet.domain.models import Asset, AssetRole
from rivet.storage.assets import AssetStore
from rivet.storage.projects import ProjectStore
from services.api.deps import get_asset_store, get_project_store

router = APIRouter(prefix="/api/projects", tags=["assets"])


@router.post("/{project_id}/assets", status_code=201)
async def upload_asset(
    project_id: str,
    role: Annotated[AssetRole, Form()],
    file: Annotated[UploadFile, File()],
    projects: ProjectStore = Depends(get_project_store),
    assets: AssetStore = Depends(get_asset_store),
) -> Asset:
    if projects.get(project_id) is None:
        raise HTTPException(status_code=404, detail="project not found")
    data = await file.read()
    try:
        media = validate_upload(role, data, file.content_type)
    except UnsupportedMediaType as error:
        raise HTTPException(status_code=415, detail=str(error)) from error
    except MediaTooLarge as error:
        raise HTTPException(status_code=413, detail=str(error)) from error
    except InvalidMedia as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    return assets.save(
        project_id,
        role,
        data,
        media.mime,
        media.suffix,
        width=media.width,
        height=media.height,
    )
