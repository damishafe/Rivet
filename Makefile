.PHONY: doctor dev dev-api dev-web test test-golden lint benchmark-cold benchmark-hot offline-demo submission-check

doctor:
	uv run rivet doctor

dev:
	@trap 'kill 0' INT; \
	uv run uvicorn services.api.main:app --reload --port 8000 & \
	(cd apps/web && npm run dev) & \
	wait

dev-api:
	uv run uvicorn services.api.main:app --reload --port 8000

dev-web:
	cd apps/web && npm run dev

test:
	uv run pytest tests/unit tests/integration

test-golden:
	uv run pytest tests/golden

lint:
	uv run ruff check .
	uv run mypy
	cd apps/web && npm run lint

FIXTURE ?= fixtures/kora-arc

benchmark-cold:
	rm -rf .benchmark/cold-0
	uv run rivet benchmark --fixture $(FIXTURE) --mode cold

benchmark-hot:
	rm -rf .benchmark/hot-0 .benchmark/hot-1
	uv run rivet benchmark --fixture $(FIXTURE) --mode hot

offline-demo:
	uv run rivet offline-demo --fixture $(FIXTURE)

submission-check:
	@echo "submission-check: not implemented until D12 (Aug 3)" && exit 1
