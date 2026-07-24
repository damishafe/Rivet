# Rivet

Verified multimodal ad creation on one AMD Radeon GPU.

A product image, brand kit and spoken brief become a verified three-scene vertical advertisement — without allowing AI to distort the product, logo or text. Built for the AMD AI DevMaster Hackathon 2026 (Track 1) on a Radeon PRO W7900 · ROCm 7.2.1.

## Quick start

```bash
uv sync
cd apps/web && npm install && cd ../..
make doctor
make dev        # FastAPI on :8000 + web studio on :5173
```

## Commands

```bash
make doctor            # environment check (GPU checks apply on the W7900 box)
make dev               # api + web dev servers
make test              # unit + integration tests
make lint              # ruff + mypy + eslint
uv run rivet --help    # CLI
```

Full README (model install, benchmarks, demo fixture, troubleshooting) lands with the release candidate.
