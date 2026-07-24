from pathlib import Path

import pytest
from sqlalchemy.engine import Engine

from rivet.storage.db import make_engine


@pytest.fixture()
def engine(tmp_path: Path) -> Engine:
    return make_engine(tmp_path / "test.db")
