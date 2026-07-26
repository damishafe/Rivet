from pathlib import Path


def _cache_root() -> Path | None:
    try:
        from huggingface_hub.constants import HF_HUB_CACHE
    except ImportError:
        return None
    root = Path(HF_HUB_CACHE)
    return root if root.is_dir() else None


def local_snapshot(repo_id: str) -> Path | None:
    root = _cache_root()
    if root is None:
        return None
    folder = root / f"models--{repo_id.replace('/', '--')}"
    snapshots = folder / "snapshots"
    if not snapshots.is_dir():
        return None
    ref = folder / "refs" / "main"
    if ref.is_file():
        pinned = snapshots / ref.read_text().strip()
        if pinned.is_dir():
            return pinned
    candidates = sorted(path for path in snapshots.iterdir() if path.is_dir())
    return candidates[-1] if candidates else None


def resolve_model(repo_id: str) -> str:
    snapshot = local_snapshot(repo_id)
    return str(snapshot) if snapshot is not None else repo_id
