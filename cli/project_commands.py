import mimetypes
from pathlib import Path

import typer
from PIL import Image

from cli.workspace import open_workspace, require_project
from rivet.adapters.heuristic_brand import propose_brand_dna
from rivet.adapters.heuristic_planner import propose_shots
from rivet.adapters.qwen_planner import propose_shots_vlm
from rivet.domain.models import AssetRole, utcnow
from rivet.storage.assets import AssetStore
from rivet.storage.plans import PlanStore
from rivet.storage.projects import ProjectStore

app = typer.Typer(no_args_is_help=True)


def _save_asset(assets: AssetStore, project_id: str, path: Path, role: AssetRole) -> None:
    if not path.is_file():
        typer.echo(f"missing {role} image: {path}", err=True)
        raise typer.Exit(code=1)
    with Image.open(path) as image:
        width, height = image.size
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    assets.save(project_id, role, path.read_bytes(), mime, path.suffix, width, height)


@app.command()
def create(name: str, seed: int | None = None) -> None:
    """Create a project and print its id."""
    engine, _ = open_workspace()
    project = ProjectStore(engine).create(name, seed)
    typer.echo(project.id)


@app.command()
def ingest(project_id: str, product: Path, logo: Path, brief: str | None = None) -> None:
    """Attach the product image, logo and optional brief text."""
    engine, root = open_workspace()
    require_project(engine, project_id)
    assets = AssetStore(engine, root)
    _save_asset(assets, project_id, product, "product")
    _save_asset(assets, project_id, logo, "logo")
    if brief:
        ProjectStore(engine).set_brief(project_id, brief)
    typer.echo(f"ingested product and logo for {project_id}")


@app.command()
def plan(project_id: str, vlm: bool = True) -> None:
    """Derive and confirm brand DNA, then propose the three-scene storyboard."""
    engine, root = open_workspace()
    project = require_project(engine, project_id)
    assets = AssetStore(engine, root)
    products = assets.find(project_id, "product")
    logos = assets.find(project_id, "logo")
    if not products or not logos:
        typer.echo("product and logo assets required — run 'rivet ingest' first", err=True)
        raise typer.Exit(code=1)
    product, logo = products[-1], logos[-1]
    dna = propose_brand_dna(
        project.name,
        product.id,
        logo.id,
        Path(product.path).read_bytes(),
        Path(logo.path).read_bytes(),
    )
    projects = ProjectStore(engine)
    confirmed = dna.model_copy(update={"confirmed_at": utcnow()})
    projects.set_brand_dna(project_id, confirmed)
    if vlm:
        shots = propose_shots_vlm(
            confirmed, project.campaign_seed, product.path, project.brief or ""
        )
    else:
        shots = propose_shots(confirmed, project.campaign_seed)
    PlanStore(engine).set_plan(project_id, shots)
    for shot in shots:
        typer.echo(f"  {shot.shot_id:<6} {shot.copy_.headline}  |  {shot.copy_.support}")
        typer.echo(f"         cta: {shot.copy_.cta}   narration: {shot.narration}")
