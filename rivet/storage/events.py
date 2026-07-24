from sqlalchemy.engine import Engine
from sqlmodel import Session, col, func, select

from rivet.domain.events import StageEvent
from rivet.storage.records import EventRow


class EventStore:
    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def append(self, event: StageEvent) -> int:
        with Session(self._engine) as session:
            current = session.exec(
                select(func.max(EventRow.seq)).where(EventRow.job_id == event.job_id)
            ).one()
            seq = (current or 0) + 1
            session.add(
                EventRow(job_id=event.job_id, seq=seq, payload=event.model_dump(mode="json"))
            )
            session.commit()
            return seq

    def list_after(self, job_id: str, after_seq: int = 0) -> list[tuple[int, StageEvent]]:
        with Session(self._engine) as session:
            rows = session.exec(
                select(EventRow)
                .where(EventRow.job_id == job_id, EventRow.seq > after_seq)
                .order_by(col(EventRow.seq))
            ).all()
            return [(row.seq, StageEvent.model_validate(row.payload)) for row in rows]
