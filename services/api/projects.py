from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, field_validator

from rivet.domain.models import Project
from rivet.storage.projects import ProjectStore
from services.api.deps import get_project_store

router = APIRouter(prefix="/api/projects", tags=["projects"])


class CreateProjectBody(BaseModel):
    name: str = Field(min_length=1, max_length=120)


class BriefBody(BaseModel):
    text: str

    @field_validator("text")
    @classmethod
    def strip_and_bound(cls, value: str) -> str:
        stripped = value.strip()
        if not 20 <= len(stripped) <= 1000:
            raise ValueError("brief must be 20-1000 characters")
        return stripped


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


@router.post("/{project_id}/brief")
def set_brief(
    project_id: str, body: BriefBody, store: ProjectStore = Depends(get_project_store)
) -> Project:
    try:
        return store.set_brief(project_id, body.text)
    except KeyError as error:
        raise HTTPException(status_code=404, detail="project not found") from error
