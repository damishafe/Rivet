from pathlib import Path

from sqlalchemy.engine import Engine
from sqlmodel import Session

from rivet.pipeline.stage import StageResult
from rivet.storage.records import StageCacheRow


class StageCacheStore:
    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def put(self, fingerprint: str, result: StageResult) -> None:
        with Session(self._engine) as session:
            row = session.get(StageCacheRow, fingerprint)
            if row is None:
                row = StageCacheRow(fingerprint=fingerprint, payload=result.model_dump(mode="json"))
            else:
                row.payload = result.model_dump(mode="json")
            session.add(row)
            session.commit()

    def get(self, fingerprint: str) -> StageResult | None:
        with Session(self._engine) as session:
            row = session.get(StageCacheRow, fingerprint)
            if row is None:
                return None
            result = StageResult.model_validate(row.payload)
        for path in result.artifacts.values():
            if not Path(path).exists():
                return None
        return result
