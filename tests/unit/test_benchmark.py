import json
from datetime import UTC, datetime, timedelta

from rivet.domain.models import AuditCheck, StageRun
from rivet.domain.receipt import CampaignReceipt, SceneResult
from rivet.telemetry.benchmark import (
    BenchmarkReport,
    RunReport,
    StageTiming,
    check_totals,
    stage_timings,
)
from rivet.telemetry.benchmark_format import to_csv, to_json, to_markdown

START = datetime(2026, 8, 2, 10, 0, 0, tzinfo=UTC)


def make_run(stage: str, seconds: float, vram: int | None, cache_hit: bool = False) -> StageRun:
    return StageRun(
        project_id="p",
        job_id="j",
        stage=stage,
        seed=7,
        started_at=START,
        finished_at=START + timedelta(seconds=seconds),
        peak_vram_mb=vram,
        status="succeeded",
        cache_hit=cache_hit,
    )


def make_report(*runs: RunReport) -> BenchmarkReport:
    return BenchmarkReport(
        fixture="fixtures/kora-arc",
        created_at="2026-08-02T10:00:00+00:00",
        environment={"device": "cuda", "accelerator": "Radeon PRO W7900"},
        runs=list(runs),
    )


def make_run_report(mode: str, receipt_hash: str) -> RunReport:
    return RunReport(
        mode=mode,
        plan_seconds=12.0,
        campaign_seconds=48.0,
        total_seconds=60.0,
        stages=[
            StageTiming("segment", 3.5, 2100, False, "succeeded"),
            StageTiming("background.hook", 9.0, 8400, False, "succeeded"),
        ],
        receipt_hash=receipt_hash,
        passed=True,
        checks_passed=27,
        checks_total=27,
        repairs=0,
    )


def test_stage_timings_measure_wall_clock_and_vram() -> None:
    timings = stage_timings([make_run("segment", 3.5, 2100), make_run("motion.hook", 1.25, None)])
    assert [t.stage for t in timings] == ["segment", "motion.hook"]
    assert timings[0].seconds == 3.5
    assert timings[0].peak_vram_mb == 2100
    assert timings[1].peak_vram_mb is None


def test_unfinished_stage_is_excluded() -> None:
    unfinished = make_run("segment", 1.0, None)
    unfinished.finished_at = None
    assert stage_timings([unfinished]) == []


def test_peak_vram_is_the_worst_stage() -> None:
    report = make_run_report("cold", "a" * 64)
    assert report.peak_vram_mb == 8400


def test_peak_vram_is_none_without_accelerator() -> None:
    report = make_run_report("cold", "a" * 64)
    report.stages = [StageTiming("segment", 1.0, None, False, "succeeded")]
    assert report.peak_vram_mb is None


def test_determinism_requires_matching_hashes_across_runs() -> None:
    same = make_report(make_run_report("warmup", "a" * 64), make_run_report("hot", "a" * 64))
    assert same.deterministic
    differing = make_report(make_run_report("warmup", "a" * 64), make_run_report("hot", "b" * 64))
    assert not differing.deterministic


def test_single_run_is_not_claimed_deterministic() -> None:
    assert not make_report(make_run_report("cold", "a" * 64)).deterministic


def test_check_totals_ignore_advisory_checks() -> None:
    def check(check_id: str, passed: bool, advisory: bool = False) -> AuditCheck:
        return AuditCheck(
            check_id=check_id, metric="m", threshold="t", observed="o",
            passed=passed, owner_stage="s", advisory=advisory,
        )

    receipt = CampaignReceipt(
        project_id="p", product_sha256="a" * 64, logo_sha256="b" * 64,
        scenes=[
            SceneResult(
                shot_id="hook", still_path="s.png", seed=1,
                checks=[check("A01", True), check("A08", False, advisory=True)],
                passed=True,
            )
        ],
        passed=True,
    )
    assert check_totals(receipt) == (1, 1)


def test_markdown_reports_environment_and_determinism() -> None:
    body = to_markdown(make_report(make_run_report("warmup", "c" * 64), make_run_report("hot", "c" * 64)))
    assert "Radeon PRO W7900" in body
    assert "identical receipt hash across runs" in body
    assert "8400 MB" in body
    assert "27/27" in body


def test_markdown_does_not_claim_determinism_on_a_single_run() -> None:
    body = to_markdown(make_report(make_run_report("cold", "c" * 64)))
    assert "not verified" in body


def test_csv_has_a_row_per_stage() -> None:
    rows = to_csv(make_report(make_run_report("cold", "d" * 64))).strip().splitlines()
    assert rows[0] == "mode,stage,seconds,peak_vram_mb,cache_hit,status"
    assert len(rows) == 3
    assert rows[1].startswith("cold,segment,3.500,2100,false")


def test_report_states_how_vram_was_measured() -> None:
    from rivet.telemetry.vram import accelerator_report, peak_mb, vram_metric

    report = accelerator_report()
    assert report["vram_metric"] == vram_metric()
    if report["device"] != "cuda":
        assert peak_mb() is None, "only cuda/rocm expose a true per-stage peak"
        assert "unavailable" in report["vram_metric"]


def test_markdown_shows_na_when_vram_is_unmeasurable() -> None:
    run = make_run_report("cold", "f" * 64)
    run.stages = [StageTiming("segment", 1.0, None, False, "succeeded")]
    body = to_markdown(make_report(run))
    assert "n/a" in body


def test_json_round_trips_with_derived_fields() -> None:
    payload = json.loads(to_json(make_report(make_run_report("cold", "e" * 64))))
    assert payload["environment"]["device"] == "cuda"
    assert payload["runs"][0]["peak_vram_mb"] == 8400
    assert payload["deterministic"] is False
