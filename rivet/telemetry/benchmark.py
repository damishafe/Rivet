from dataclasses import asdict, dataclass, field

from rivet.domain.models import StageRun
from rivet.domain.receipt import CampaignReceipt


@dataclass
class StageTiming:
    stage: str
    seconds: float
    peak_vram_mb: int | None
    cache_hit: bool
    status: str


@dataclass
class RunReport:
    mode: str
    plan_seconds: float
    campaign_seconds: float
    total_seconds: float
    stages: list[StageTiming]
    receipt_hash: str
    passed: bool
    checks_passed: int
    checks_total: int
    repairs: int

    @property
    def peak_vram_mb(self) -> int | None:
        seen = [s.peak_vram_mb for s in self.stages if s.peak_vram_mb is not None]
        return max(seen) if seen else None


@dataclass
class BenchmarkReport:
    fixture: str
    created_at: str
    environment: dict[str, str]
    runs: list[RunReport] = field(default_factory=list)

    @property
    def deterministic(self) -> bool:
        hashes = {run.receipt_hash for run in self.runs if run.receipt_hash}
        return len(hashes) == 1 and len(self.runs) > 1

    def as_dict(self) -> dict[str, object]:
        return {
            "fixture": self.fixture,
            "created_at": self.created_at,
            "environment": self.environment,
            "deterministic": self.deterministic,
            "runs": [
                {**asdict(run), "peak_vram_mb": run.peak_vram_mb} for run in self.runs
            ],
        }


def stage_timings(runs: list[StageRun]) -> list[StageTiming]:
    timings: list[StageTiming] = []
    for run in runs:
        if run.finished_at is None:
            continue
        seconds = (run.finished_at - run.started_at).total_seconds()
        timings.append(
            StageTiming(
                stage=run.stage,
                seconds=round(seconds, 3),
                peak_vram_mb=run.peak_vram_mb,
                cache_hit=run.cache_hit,
                status=run.status,
            )
        )
    return timings


def check_totals(receipt: CampaignReceipt) -> tuple[int, int]:
    checks = [check for scene in receipt.scenes for check in scene.checks]
    deterministic = [check for check in checks if not check.advisory]
    return sum(1 for check in deterministic if check.passed), len(deterministic)
