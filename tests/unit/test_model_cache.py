from pathlib import Path

import pytest

from rivet.adapters import model_cache


def build_cache(root: Path, repo_id: str, commit: str, with_ref: bool = True) -> Path:
    folder = root / f"models--{repo_id.replace('/', '--')}"
    snapshot = folder / "snapshots" / commit
    snapshot.mkdir(parents=True)
    (snapshot / "model_index.json").write_text("{}")
    if with_ref:
        ref = folder / "refs" / "main"
        ref.parent.mkdir(parents=True)
        ref.write_text(commit)
    return snapshot


def test_resolves_the_snapshot_named_by_refs_main(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    wanted = build_cache(tmp_path, "stabilityai/stable-diffusion-xl-base-1.0", "aaa111")
    stale = tmp_path / "models--stabilityai--stable-diffusion-xl-base-1.0" / "snapshots" / "zzz999"
    stale.mkdir(parents=True)
    monkeypatch.setattr(model_cache, "_cache_root", lambda: tmp_path)
    resolved = model_cache.local_snapshot("stabilityai/stable-diffusion-xl-base-1.0")
    assert resolved == wanted, "must follow refs/main, not alphabetical order"


def test_falls_back_to_a_snapshot_without_refs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    snapshot = build_cache(tmp_path, "facebook/sam2.1-hiera-small", "bbb222", with_ref=False)
    monkeypatch.setattr(model_cache, "_cache_root", lambda: tmp_path)
    assert model_cache.local_snapshot("facebook/sam2.1-hiera-small") == snapshot


def test_uncached_repo_resolves_to_the_repo_id(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(model_cache, "_cache_root", lambda: tmp_path)
    assert model_cache.local_snapshot("openai/whisper-tiny.en") is None
    assert model_cache.resolve_model("openai/whisper-tiny.en") == "openai/whisper-tiny.en"


def test_resolve_returns_a_local_path_when_cached(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    snapshot = build_cache(tmp_path, "Qwen/Qwen3-VL-4B-Instruct", "ccc333")
    monkeypatch.setattr(model_cache, "_cache_root", lambda: tmp_path)
    assert model_cache.resolve_model("Qwen/Qwen3-VL-4B-Instruct") == str(snapshot)


def test_missing_cache_root_is_not_an_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(model_cache, "_cache_root", lambda: None)
    assert model_cache.resolve_model("any/model") == "any/model"
