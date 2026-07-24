import importlib.util

from rivet.pipeline.device import resolve_device


def test_resolves_to_known_device() -> None:
    assert resolve_device() in ("cuda", "mps", "cpu")


def test_without_torch_resolves_cpu(monkeypatch: object) -> None:
    import pytest

    assert isinstance(monkeypatch, pytest.MonkeyPatch)
    monkeypatch.setattr(importlib.util, "find_spec", lambda name: None)
    assert resolve_device() == "cpu"
