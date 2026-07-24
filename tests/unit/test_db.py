from pathlib import Path

from sqlalchemy import inspect
from sqlalchemy.engine import Engine

from rivet.storage.db import data_dir, make_engine


def test_make_engine_creates_all_tables(engine: Engine) -> None:
    tables = set(inspect(engine).get_table_names())
    assert {"projects", "assets", "events"} <= tables


def test_make_engine_creates_parent_dirs(tmp_path: Path) -> None:
    nested = tmp_path / "deep" / "nested" / "rivet.db"
    make_engine(nested)
    assert nested.exists()


def test_data_dir_reads_env(monkeypatch: object) -> None:
    import pytest

    mp = monkeypatch
    assert isinstance(mp, pytest.MonkeyPatch)
    mp.setenv("RIVET_DATA_DIR", "/tmp/rivet-test-data")
    assert data_dir() == Path("/tmp/rivet-test-data")


def test_engine_uses_wal_and_busy_timeout(engine: Engine) -> None:
    with engine.connect() as conn:
        journal = conn.exec_driver_sql("PRAGMA journal_mode").scalar()
        timeout = conn.exec_driver_sql("PRAGMA busy_timeout").scalar()
    assert journal == "wal"
    assert timeout == 30000
