import asyncio
import time
from datetime import UTC, datetime
from pathlib import Path

import typer

from rivet.pipeline.bootstrap import confirm_brand, derive_plan, ingest_asset
from rivet.pipeline.campaign import run_campaign
from rivet.storage.assets import AssetStore
from rivet.storage.db import make_engine
from rivet.storage.projects import ProjectStore
from rivet.storage.stage_runs import StageRunStore
from rivet.telemetry.benchmark import (
    BenchmarkReport,
    RunReport,
    check_totals,
    stage_timings,
)
from rivet.telemetry.benchmark_format import to_csv, to_json, to_markdown
from rivet.telemetry.vram import accelerator_report

BENCHMARK_SEED = 7


def _one_run(root: Path, fixture: Path, mode: str, vlm: bool, semantic: bool) -> RunReport:
    engine = make_engine(root / "rivet.db")
    projects = ProjectStore(engine)
    assets = AssetStore(engine, root)
    project = projects.create("Rivet benchmark", campaign_seed=BENCHMARK_SEED)

    product = ingest_asset(assets, project.id, fixture / "product.png", "product")
    logo = ingest_asset(assets, project.id, fixture / "logo.png", "logo")
    confirm_brand(engine, root, project.id, product, logo)

    plan_started = time.perf_counter()
    derive_plan(engine, project.id, product.path, use_vlm=vlm)
    plan_seconds = time.perf_counter() - plan_started

    campaign_started = time.perf_counter()
    receipt = asyncio.run(run_campaign(engine, root, project.id, semantic=semantic))
    campaign_seconds = time.perf_counter() - campaign_started

    passed, total = check_totals(receipt)
    return RunReport(
        mode=mode,
        plan_seconds=round(plan_seconds, 3),
        campaign_seconds=round(campaign_seconds, 3),
        total_seconds=round(plan_seconds + campaign_seconds, 3),
        stages=stage_timings(StageRunStore(engine).list_for_project(project.id)),
        receipt_hash=receipt.receipt_hash,
        passed=receipt.passed,
        checks_passed=passed,
        checks_total=total,
        repairs=len(receipt.repairs),
    )


def benchmark(
    fixture: Path = Path("fixtures/kora-arc"),
    mode: str = "cold",
    out: Path = Path("docs/benchmarks"),
    workdir: Path = Path(".benchmark"),
    vlm: bool = True,
    semantic: bool = False,
) -> None:
    """Measure the pipeline end to end and write JSON, CSV and Markdown evidence."""
    if mode not in ("cold", "hot"):
        typer.echo("mode must be cold or hot", err=True)
        raise typer.Exit(code=2)
    for required in ("product.png", "logo.png"):
        if not (fixture / required).is_file():
            typer.echo(f"fixture is missing {required}: {fixture}", err=True)
            raise typer.Exit(code=1)

    report = BenchmarkReport(
        fixture=str(fixture),
        created_at=datetime.now(UTC).isoformat(timespec="seconds"),
        environment=accelerator_report(),
    )
    passes = ["cold"] if mode == "cold" else ["warmup", "hot"]
    for index, label in enumerate(passes):
        root = workdir / f"{mode}-{index}"
        typer.echo(f"running {label} pass in {root}")
        run = _one_run(root, fixture, label, vlm, semantic)
        report.runs.append(run)
        typer.echo(
            f"  {label}: total {run.total_seconds:.1f}s  "
            f"checks {run.checks_passed}/{run.checks_total}  passed={run.passed}"
        )

    out.mkdir(parents=True, exist_ok=True)
    (out / f"benchmark-{mode}.json").write_text(to_json(report))
    (out / f"benchmark-{mode}.csv").write_text(to_csv(report))
    (out / f"benchmark-{mode}.md").write_text(to_markdown(report))
    typer.echo(f"wrote {out}/benchmark-{mode}.[json|csv|md]")
    if not all(run.passed for run in report.runs):
        typer.echo("benchmark completed with a failing audit", err=True)
        raise typer.Exit(code=3)
