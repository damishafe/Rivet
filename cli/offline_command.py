import asyncio
import os
import shutil
from pathlib import Path

import typer

from rivet.pipeline.bootstrap import confirm_brand, derive_plan, ingest_asset
from rivet.pipeline.campaign import run_campaign
from rivet.storage.assets import AssetStore
from rivet.storage.db import make_engine
from rivet.storage.projects import ProjectStore
from rivet.telemetry.network_guard import OFFLINE_ENV, block_outbound

OFFLINE_SEED = 7


def offline_demo(
    fixture: Path = Path("fixtures/kora-arc"),
    workdir: Path = Path(".benchmark/offline"),
    vlm: bool = True,
    semantic: bool = False,
) -> None:
    """Run the golden project with every outbound socket blocked (release gate G2)."""
    for required in ("product.png", "logo.png"):
        if not (fixture / required).is_file():
            typer.echo(f"fixture is missing {required}: {fixture}", err=True)
            raise typer.Exit(code=1)
    for key, value in OFFLINE_ENV.items():
        os.environ[key] = value
    if workdir.exists():
        shutil.rmtree(workdir)

    engine = make_engine(workdir / "rivet.db")
    projects = ProjectStore(engine)
    assets = AssetStore(engine, workdir)
    project = projects.create("Rivet offline demo", campaign_seed=OFFLINE_SEED)

    typer.echo("outbound network blocked; running the golden project")
    with block_outbound() as attempts:
        product = ingest_asset(assets, project.id, fixture / "product.png", "product")
        logo = ingest_asset(assets, project.id, fixture / "logo.png", "logo")
        confirm_brand(engine, workdir, project.id, product, logo)
        derive_plan(engine, project.id, product.path, use_vlm=vlm)
        receipt = asyncio.run(run_campaign(engine, workdir, project.id, semantic=semantic))

    checks = [check for scene in receipt.scenes for check in scene.checks if not check.advisory]
    passed = sum(1 for check in checks if check.passed)
    typer.echo(f"  checks {passed}/{len(checks)}  passed={receipt.passed}")
    typer.echo(f"  receipt {receipt.receipt_hash[:16]}")
    typer.echo(f"  pack {receipt.pack_path}")
    typer.echo(f"  outbound attempts blocked: {len(attempts)}")
    if not receipt.passed or receipt.pack_path is None:
        typer.echo("offline demo did not produce a passing export", err=True)
        raise typer.Exit(code=3)
    typer.echo("G2 offline gate: pass")
