import pytest

from rivet.adapters import residency


@pytest.fixture(autouse=True)
def clean_residency() -> None:
    residency.release_all()


def test_second_acquire_reuses_the_resident_model() -> None:
    loads = []

    def loader() -> str:
        loads.append(1)
        return "sdxl"

    first = residency.acquire("sdxl:cuda", loader)
    second = residency.acquire("sdxl:cuda", loader)

    assert first is second
    assert len(loads) == 1
    event = residency.last_acquisition()
    assert event is not None and event.resident


def test_a_different_model_evicts_the_previous_one() -> None:
    loads: list[str] = []

    residency.acquire("sdxl:cuda", lambda: loads.append("sdxl") or "sdxl")
    residency.acquire("kokoro:cuda", lambda: loads.append("kokoro") or "kokoro")
    residency.acquire("sdxl:cuda", lambda: loads.append("sdxl") or "sdxl")

    assert loads == ["sdxl", "kokoro", "sdxl"]


def test_disabled_residency_reloads_every_time(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(residency.ENV_FLAG, "0")
    loads = []

    def loader() -> str:
        loads.append(1)
        return "sdxl"

    residency.acquire("sdxl:cuda", loader)
    residency.acquire("sdxl:cuda", loader)

    assert len(loads) == 2
    event = residency.last_acquisition()
    assert event is not None and not event.resident
