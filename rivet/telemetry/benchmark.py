import hashlib
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

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
    content_digest: str
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
        digests = {run.content_digest for run in self.runs if run.content_digest}
        return len(digests) == 1 and len(self.runs) > 1

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


def content_digest(receipt: CampaignReceipt) -> str:
    payload = []
    for scene in receipt.scenes:
        still = Path(scene.still_path)
        payload.append(
            {
                "shot_id": scene.shot_id,
                "seed": scene.seed,
                "still_sha256": (
                    hashlib.sha256(still.read_bytes()).hexdigest() if still.is_file() else None
                ),
                "checks": [
                    [check.check_id, str(check.observed), check.passed]
                    for check in scene.checks
                    if not check.advisory
                ],
            }
        )
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def check_totals(receipt: CampaignReceipt) -> tuple[int, int]:
    checks = [check for scene in receipt.scenes for check in scene.checks]
    deterministic = [check for check in checks if not check.advisory]
    return sum(1 for check in deterministic if check.passed), len(deterministic)
