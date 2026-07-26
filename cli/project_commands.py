from pathlib import Path

import typer

from cli.workspace import open_workspace, require_project
from rivet.domain.models import AssetRole
from rivet.pipeline.bootstrap import confirm_brand, derive_plan, ingest_asset
from rivet.storage.assets import AssetStore
from rivet.storage.projects import ProjectStore

app = typer.Typer(no_args_is_help=True)


def _save_asset(assets: AssetStore, project_id: str, path: Path, role: AssetRole) -> None:
    if not path.is_file():
        typer.echo(f"missing {role} image: {path}", err=True)
        raise typer.Exit(code=1)
    ingest_asset(assets, project_id, path, role)


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
    require_project(engine, project_id)
    assets = AssetStore(engine, root)
    products = assets.find(project_id, "product")
    logos = assets.find(project_id, "logo")
    if not products or not logos:
        typer.echo("product and logo assets required — run 'rivet ingest' first", err=True)
        raise typer.Exit(code=1)
    product, logo = products[-1], logos[-1]
    confirm_brand(engine, root, project_id, product, logo)
    shots = derive_plan(engine, project_id, product.path, use_vlm=vlm)
    for shot in shots:
        typer.echo(f"  {shot.shot_id:<6} {shot.copy_.headline}  |  {shot.copy_.support}")
        typer.echo(f"         cta: {shot.copy_.cta}   narration: {shot.narration}")
