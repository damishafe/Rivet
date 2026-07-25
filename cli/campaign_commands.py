import asyncio
import shutil
from pathlib import Path

import typer

from cli.workspace import campaign_dir, open_workspace
from rivet.domain.receipt import CampaignReceipt
from rivet.pipeline.campaign import run_campaign
from rivet.pipeline.campaign_inputs import (
    CampaignConflict,
    CampaignFailed,
    CampaignNotFound,
)

app = typer.Typer(no_args_is_help=True)


def _print_receipt(receipt: CampaignReceipt) -> None:
    for scene in receipt.scenes:
        for check in scene.checks:
            mark = "ok" if check.passed else ("warn" if check.advisory else "FAIL")
            typer.echo(f"  [{mark:>4}] {scene.shot_id:<6} {check.check_id} {check.metric}")
    typer.echo(f"receipt {receipt.receipt_hash[:16]} passed={receipt.passed}")
    if receipt.repairs:
        for repair in receipt.repairs:
            typer.echo(f"  repaired {repair.shot_id}: {repair.detail} -> {repair.after_passed}")


@app.command()
def run(project_id: str, semantic: bool = True) -> None:
    """Generate, audit, repair and render the campaign; writes the export pack."""
    engine, root = open_workspace()
    try:
        receipt = asyncio.run(
            run_campaign(engine, root, project_id, semantic=semantic)
        )
    except CampaignNotFound as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(code=1) from error
    except (CampaignConflict, CampaignFailed) as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(code=2) from error
    _print_receipt(receipt)
    if receipt.pack_path:
        typer.echo(f"pack {receipt.pack_path}")
    if not receipt.passed:
        raise typer.Exit(code=3)


@app.command()
def export(project_id: str, dest: Path) -> None:
    """Copy the campaign export pack to a destination path."""
    _, root = open_workspace()
    pack = campaign_dir(root, project_id) / "campaign-pack.zip"
    if not pack.is_file():
        typer.echo(f"no export pack for {project_id} — run 'rivet run' first", err=True)
        raise typer.Exit(code=1)
    destination = dest / pack.name if dest.is_dir() else dest
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(pack, destination)
    typer.echo(str(destination))
