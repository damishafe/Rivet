#!/usr/bin/env bash
# Produce every official number for the submission, on the Radeon box, in one run.
#
# Each stage writes its evidence under docs/evidence or docs/benchmarks and is committed
# as soon as it finishes, so an instance that dies mid-run never costs work already paid for.
# Ordered cheapest-first: a broken environment fails in seconds, not after the benchmarks.
set -uo pipefail

cd "$(dirname "$0")/../.."
mkdir -p docs/evidence

FIXTURE="${FIXTURE:-fixtures/kora-arc}"
STAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
LOG=docs/evidence/run.log
FAILED=0

say() { printf '\n=== %s ===\n' "$1" | tee -a "$LOG"; }

step() {
  local name="$1" out="$2"
  shift 2
  say "$name"
  local started
  started=$(date +%s)
  if "$@" >"$out" 2>&1; then
    echo "  ok in $(($(date +%s) - started))s → $out" | tee -a "$LOG"
  else
    echo "  FAILED in $(($(date +%s) - started))s → $out" | tee -a "$LOG"
    tail -20 "$out" | sed 's/^/    /' | tee -a "$LOG"
    FAILED=1
  fi
}

keep() {
  git add -A docs/evidence docs/benchmarks 2>/dev/null || true
  git -c user.name="${GIT_NAME:-rivet}" -c user.email="${GIT_EMAIL:-rivet@local}" \
    commit -q -m "evidence: $1 on the W7900" 2>/dev/null || true
  git push -q 2>/dev/null && echo "  pushed" || echo "  (push skipped)"
}

echo "Rivet evidence run — $STAMP" >"$LOG"

step "environment" docs/evidence/doctor.txt rivet doctor
step "accelerator" docs/evidence/accelerator.txt python -c \
  "import json;from rivet.telemetry.vram import accelerator_report;print(json.dumps(accelerator_report(),indent=2))"
keep "environment"

step "unit and integration tests" docs/evidence/tests.txt uv run pytest -q
step "determinism (golden)" docs/evidence/golden.txt uv run pytest tests/golden -q
step "submission gates" docs/evidence/submission-check.txt rivet submission-check
keep "tests and gates"

step "offline gate G2" docs/evidence/offline-demo.txt \
  rivet offline-demo --fixture "$FIXTURE" --workdir .evidence/offline
keep "offline gate"

step "benchmark cold" docs/evidence/benchmark-cold.txt \
  rivet benchmark --fixture "$FIXTURE" --mode cold --workdir .evidence/cold
keep "cold benchmark"

step "benchmark hot (determinism across runs)" docs/evidence/benchmark-hot.txt \
  rivet benchmark --fixture "$FIXTURE" --mode hot --workdir .evidence/hot
keep "hot benchmark"

step "model residency A/B" docs/evidence/benchmark-residency.txt \
  rivet benchmark --fixture "$FIXTURE" --mode residency --workdir .evidence/residency
keep "residency benchmark"

say "summary"
grep -E "^  (ok|FAILED)" "$LOG" | tee -a "$LOG"
if [ "$FAILED" -ne 0 ]; then
  echo "some stages failed — see docs/evidence" | tee -a "$LOG"
  exit 1
fi
echo "all evidence produced" | tee -a "$LOG"
