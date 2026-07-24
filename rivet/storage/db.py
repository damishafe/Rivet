import os
from pathlib import Path

from sqlalchemy.engine import Engine
from sqlmodel import SQLModel, create_engine

import rivet.storage.records  # noqa: F401


def data_dir() -> Path:
    return Path(os.environ.get("RIVET_DATA_DIR", "data"))


def make_engine(db_path: Path | None = None) -> Engine:
    path = db_path if db_path is not None else data_dir() / "rivet.db"
    path.parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(
        f"sqlite:///{path}", connect_args={"check_same_thread": False}
    )
    SQLModel.metadata.create_all(engine)
    return engine
