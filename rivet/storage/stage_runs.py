from sqlalchemy.engine import Engine
from sqlmodel import Session, select

from rivet.domain.models import StageRun
from rivet.storage.records import StageRunRow


class StageRunStore:
    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def add(self, run: StageRun) -> None:
        with Session(self._engine) as session:
            session.add(
                StageRunRow(
                    id=run.id,
                    job_id=run.job_id,
                    project_id=run.project_id,
                    payload=run.model_dump(mode="json"),
                )
            )
            session.commit()

    def list_for_job(self, job_id: str) -> list[StageRun]:
        with Session(self._engine) as session:
            rows = session.exec(
                select(StageRunRow).where(StageRunRow.job_id == job_id)
            ).all()
        runs = [StageRun.model_validate(row.payload) for row in rows]
        return sorted(runs, key=lambda run: run.started_at)
