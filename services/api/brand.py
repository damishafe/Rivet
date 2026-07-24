from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException

from rivet.adapters.heuristic_brand import propose_brand_dna
from rivet.domain.models import BrandDNA, Project, utcnow
from rivet.storage.assets import AssetStore
from rivet.storage.projects import ProjectStore
from services.api.deps import get_asset_store, get_project_store

router = APIRouter(prefix="/api/projects", tags=["brand"])


def _require_project(store: ProjectStore, project_id: str) -> Project:
    project = store.get(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="project not found")
    return project


@router.post("/{project_id}/brand/derive")
def derive_brand(
    project_id: str,
    projects: ProjectStore = Depends(get_project_store),
    assets: AssetStore = Depends(get_asset_store),
) -> BrandDNA:
    project = _require_project(projects, project_id)
    products = assets.find(project_id, "product")
    logos = assets.find(project_id, "logo")
    if not products or not logos:
        raise HTTPException(status_code=409, detail="product and logo assets required")
    product = products[-1]
    image_bytes = Path(product.path).read_bytes()
    return propose_brand_dna(project.name, product.id, logos[-1].id, image_bytes)


@router.put("/{project_id}/brand")
def confirm_brand(
    project_id: str,
    dna: BrandDNA,
    projects: ProjectStore = Depends(get_project_store),
) -> Project:
    _require_project(projects, project_id)
    confirmed = dna.model_copy(update={"confirmed_at": utcnow()})
    return projects.set_brand_dna(project_id, confirmed)


@router.get("/{project_id}/brand")
def get_brand(
    project_id: str, projects: ProjectStore = Depends(get_project_store)
) -> BrandDNA:
    _require_project(projects, project_id)
    dna = projects.get_brand_dna(project_id)
    if dna is None:
        raise HTTPException(status_code=404, detail="brand dna not set")
    return dna
