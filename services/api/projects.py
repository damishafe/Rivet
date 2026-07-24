from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from rivet.domain.models import Project
from rivet.storage.projects import ProjectStore
from services.api.deps import get_project_store

router = APIRouter(prefix="/api/projects", tags=["projects"])


class CreateProjectBody(BaseModel):
    name: str = Field(min_length=1, max_length=120)


@router.post("", status_code=201)
def create_project(
    body: CreateProjectBody, store: ProjectStore = Depends(get_project_store)
) -> Project:
    return store.create(body.name)


@router.get("/{project_id}")
def get_project(
    project_id: str, store: ProjectStore = Depends(get_project_store)
) -> Project:
    project = store.get(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="project not found")
    return project
