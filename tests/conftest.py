from pathlib import Path

import pytest
from sqlalchemy.engine import Engine

from rivet.storage.db import make_engine


@pytest.fixture(autouse=True)
def offline_planner(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RIVET_NO_VLM", "1")


@pytest.fixture()
def engine(tmp_path: Path) -> Engine:
    return make_engine(tmp_path / "test.db")
