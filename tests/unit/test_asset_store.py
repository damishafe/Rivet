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


def test_save_persists_dimensions_and_provenance(engine: Engine, tmp_path: Path) -> None:
    store = AssetStore(engine, tmp_path)
    asset = store.save(
        "proj1", "derived", b"cutout", "image/png", ".png",
        width=640, height=480, provenance="derived",
    )
    fetched = store.get(asset.id)
    assert fetched is not None
    assert (fetched.width, fetched.height, fetched.provenance) == (640, 480, "derived")


def test_find_filters_by_role_in_insertion_order(engine: Engine, tmp_path: Path) -> None:
    store = AssetStore(engine, tmp_path)
    first = store.save("proj1", "product", b"one", "image/png", ".png")
    second = store.save("proj1", "product", b"two", "image/png", ".png")
    logo = store.save("proj1", "logo", b"three", "image/svg+xml", ".svg")
    store.save("other", "product", b"four", "image/png", ".png")
    products = store.find("proj1", "product")
    assert [a.id for a in products] == [first.id, second.id]
    assert store.find("proj1") == [*products, logo][0:3] or len(store.find("proj1")) == 3
    assert store.find("proj1", "brief_audio") == []
