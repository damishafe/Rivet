import hashlib
from pathlib import Path

from sqlalchemy.engine import Engine

from rivet.storage.assets import AssetStore


def test_save_writes_content_addressed_file(engine: Engine, tmp_path: Path) -> None:
    store = AssetStore(engine, tmp_path)
    data = b"fake png bytes"
    digest = hashlib.sha256(data).hexdigest()
    asset = store.save("proj1", "product", data, "image/png", ".png")
    assert asset.sha256 == digest
    saved = Path(asset.path)
    assert saved.read_bytes() == data
    assert saved.name == f"{digest}.png"
    assert saved.parent.name == digest[:2]
    assert not list(saved.parent.glob("*.tmp"))


def test_save_then_get_round_trips(engine: Engine, tmp_path: Path) -> None:
    store = AssetStore(engine, tmp_path)
    asset = store.save("proj1", "logo", b"logo bytes", "image/svg+xml", ".svg")
    assert store.get(asset.id) == asset


def test_same_content_maps_to_same_path(engine: Engine, tmp_path: Path) -> None:
    store = AssetStore(engine, tmp_path)
    first = store.save("proj1", "product", b"dup", "image/png", ".png")
    second = store.save("proj1", "style_ref", b"dup", "image/png", ".png")
    assert first.path == second.path
    assert first.id != second.id


def test_get_unknown_returns_none(engine: Engine, tmp_path: Path) -> None:
    assert AssetStore(engine, tmp_path).get("missing") is None
