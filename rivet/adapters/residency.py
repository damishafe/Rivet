import gc
import os
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

ENV_FLAG = "RIVET_MODEL_RESIDENCY"


@dataclass(frozen=True)
class Acquisition:
    key: str
    resident: bool
    load_seconds: float


_resident: dict[str, Any] = {}
_last: Acquisition | None = None


def enabled() -> bool:
    return os.environ.get(ENV_FLAG, "1") not in {"0", "false", "off"}


def last_acquisition() -> Acquisition | None:
    return _last


def _free_accelerator() -> None:
    gc.collect()
    try:
        import torch
    except ImportError:
        return
    if torch.cuda.is_available():
        torch.cuda.empty_cache()


def release_all() -> None:
    if not _resident:
        return
    _resident.clear()
    _free_accelerator()


def acquire(key: str, loader: Callable[[], Any]) -> Any:
    global _last
    held = _resident.get(key)
    if held is not None:
        _last = Acquisition(key=key, resident=True, load_seconds=0.0)
        return held
    release_all()
    started = time.perf_counter()
    model = loader()
    elapsed = time.perf_counter() - started
    _last = Acquisition(key=key, resident=False, load_seconds=elapsed)
    if enabled():
        _resident[key] = model
    return model
