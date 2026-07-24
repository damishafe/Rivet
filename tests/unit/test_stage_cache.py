from pathlib import Path

from sqlalchemy.engine import Engine

from rivet.pipeline.stage import StageResult
from rivet.storage.stage_cache import StageCacheStore


def test_put_get_round_trip(engine: Engine, tmp_path: Path) -> None:
    artifact = tmp_path / "out.png"
    artifact.write_bytes(b"data")
    store = StageCacheStore(engine)
    result = StageResult(artifacts={"image": str(artifact)}, metrics={"steps": 4.0})
    store.put("f" * 64, result)
    assert store.get("f" * 64) == result


def test_get_missing_returns_none(engine: Engine) -> None:
    assert StageCacheStore(engine).get("0" * 64) is None


def test_stale_artifact_invalidates_entry(engine: Engine, tmp_path: Path) -> None:
    artifact = tmp_path / "gone.png"
    artifact.write_bytes(b"data")
    store = StageCacheStore(engine)
    store.put("a" * 64, StageResult(artifacts={"image": str(artifact)}))
    artifact.unlink()
    assert store.get("a" * 64) is None


def test_put_overwrites_existing(engine: Engine, tmp_path: Path) -> None:
    artifact = tmp_path / "v2.png"
    artifact.write_bytes(b"data")
    store = StageCacheStore(engine)
    store.put("b" * 64, StageResult(artifacts={}))
    store.put("b" * 64, StageResult(artifacts={"image": str(artifact)}))
    fetched = store.get("b" * 64)
    assert fetched is not None and "image" in fetched.artifacts
