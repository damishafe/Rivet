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

benchmark-cold:
	@echo "benchmark-cold: not implemented until D11 (Aug 2)" && exit 1

benchmark-hot:
	@echo "benchmark-hot: not implemented until D11 (Aug 2)" && exit 1

offline-demo:
	@echo "offline-demo: not implemented until D12 (Aug 3)" && exit 1

submission-check:
	@echo "submission-check: not implemented until D12 (Aug 3)" && exit 1
