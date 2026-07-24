import hashlib
import json
from typing import Any

from rivet.pipeline.stage import ModelManifest, StageRequest


def canonical(payload: dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)


def cache_key(
    stage: str, version: str, request: StageRequest, manifest: ModelManifest | None
) -> str:
    payload: dict[str, Any] = {
        "stage": stage,
        "version": version,
        "seed": request.seed,
        "config": request.config,
        "inputs": sorted(request.input_hashes),
        "model": manifest.model_dump() if manifest else None,
    }
    return hashlib.sha256(canonical(payload).encode()).hexdigest()
