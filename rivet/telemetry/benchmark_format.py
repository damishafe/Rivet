import csv
import io
import json

from rivet.telemetry.benchmark import BenchmarkReport


def to_json(report: BenchmarkReport) -> str:
    return json.dumps(report.as_dict(), indent=2, sort_keys=True)


def to_csv(report: BenchmarkReport) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(["mode", "stage", "seconds", "peak_vram_mb", "cache_hit", "status"])
    for run in report.runs:
        for stage in run.stages:
            writer.writerow(
                [
                    run.mode,
                    stage.stage,
                    f"{stage.seconds:.3f}",
                    "" if stage.peak_vram_mb is None else stage.peak_vram_mb,
                    "true" if stage.cache_hit else "false",
                    stage.status,
                ]
            )
    return buffer.getvalue()


def _vram(value: int | None) -> str:
    return "n/a" if value is None else f"{value} MB"


def to_markdown(report: BenchmarkReport) -> str:
    lines = [
        "# Rivet benchmark",
        "",
        f"- fixture: `{report.fixture}`",
        f"- generated: {report.created_at}",
    ]
    lines += [f"- {key}: {value}" for key, value in sorted(report.environment.items())]
    lines += [
        "",
        "## Runs",
        "",
        "| mode | plan s | campaign s | total s | peak VRAM | checks | repairs | content |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for run in report.runs:
        lines.append(
            f"| {run.mode} | {run.plan_seconds:.1f} | {run.campaign_seconds:.1f} "
            f"| {run.total_seconds:.1f} | {_vram(run.peak_vram_mb)} "
            f"| {run.checks_passed}/{run.checks_total} | {run.repairs} "
            f"| `{run.content_digest[:16]}` |"
        )
    verdict = (
        "identical stills and audit observations across runs"
        if report.deterministic
        else "not verified"
    )
    lines += ["", f"**Determinism:** {verdict}", "", "## Stages", ""]
    for run in report.runs:
        lines += [
            f"### {run.mode}",
            "",
            "| stage | seconds | peak VRAM | cache |",
            "| --- | ---: | ---: | --- |",
        ]
        for stage in run.stages:
            cache = "hit" if stage.cache_hit else "miss"
            lines.append(
                f"| {stage.stage} | {stage.seconds:.2f} | {_vram(stage.peak_vram_mb)} | {cache} |"
            )
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"
