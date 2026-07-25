from pathlib import Path

import typer
from sqlalchemy.engine import Engine

from rivet.domain.models import Project
from rivet.storage.db import data_dir, make_engine
from rivet.storage.projects import ProjectStore


def open_workspace() -> tuple[Engine, Path]:
    root = data_dir()
    return make_engine(root / "rivet.db"), root


def require_project(engine: Engine, project_id: str) -> Project:
    project = ProjectStore(engine).get(project_id)
    if project is None:
        typer.echo(f"project not found: {project_id}", err=True)
        raise typer.Exit(code=1)
    return project


def campaign_dir(root: Path, project_id: str) -> Path:
    return root / "projects" / project_id / "work" / "campaign"
