import mimetypes
from pathlib import Path

from PIL import Image
from sqlalchemy.engine import Engine

from rivet.adapters.heuristic_brand import propose_brand_dna
from rivet.adapters.heuristic_planner import propose_shots
from rivet.adapters.qwen_planner import SceneWriter, propose_shots_vlm
from rivet.domain.models import Asset, AssetRole, ShotPlan, utcnow
from rivet.storage.assets import AssetStore
from rivet.storage.plans import PlanStore
from rivet.storage.projects import ProjectStore


def ingest_asset(assets: AssetStore, project_id: str, path: Path, role: AssetRole) -> Asset:
    with Image.open(path) as image:
        width, height = image.size
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    return assets.save(project_id, role, path.read_bytes(), mime, path.suffix, width, height)


def confirm_brand(
    engine: Engine, root: Path, project_id: str, product: Asset, logo: Asset
) -> None:
    projects = ProjectStore(engine)
    project = projects.get(project_id)
    if project is None:
        raise KeyError(project_id)
    dna = propose_brand_dna(
        project.name,
        product.id,
        logo.id,
        Path(product.path).read_bytes(),
        Path(logo.path).read_bytes(),
    )
    projects.set_brand_dna(project_id, dna.model_copy(update={"confirmed_at": utcnow()}))


def derive_plan(
    engine: Engine,
    project_id: str,
    product_path: str,
    use_vlm: bool = True,
    writer: SceneWriter | None = None,
) -> list[ShotPlan]:
    projects = ProjectStore(engine)
    project = projects.get(project_id)
    dna = projects.get_brand_dna(project_id)
    if project is None or dna is None:
        raise KeyError(project_id)
    if use_vlm:
        shots = propose_shots_vlm(
            dna, project.campaign_seed, product_path, project.brief or "", writer
        )
    else:
        shots = propose_shots(dna, project.campaign_seed)
    PlanStore(engine).set_plan(project_id, shots)
    return shots
