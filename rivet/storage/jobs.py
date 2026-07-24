from sqlalchemy.engine import Engine
from sqlmodel import Session, col, select

from rivet.domain.jobs import Job, JobStatus
from rivet.domain.models import utcnow
from rivet.storage.projects import _aware
from rivet.storage.records import JobRow

ACTIVE_STATUSES = ("queued", "running")


class ActiveJobError(Exception):
    def __init__(self, project_id: str) -> None:
        super().__init__(f"project {project_id} already has an active job")
        self.project_id = project_id


def _to_job(row: JobRow) -> Job:
    return Job.model_validate(
        {
            "id": row.id,
            "project_id": row.project_id,
            "kind": row.kind,
            "status": row.status,
            "error": row.error,
            "created_at": _aware(row.created_at),
            "updated_at": _aware(row.updated_at),
        }
    )


class JobStore:
    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def create(self, project_id: str, kind: str) -> Job:
        job = Job(project_id=project_id, kind=kind)
        with Session(self._engine) as session:
            active = session.exec(
                select(JobRow).where(
                    JobRow.project_id == project_id,
                    col(JobRow.status).in_(ACTIVE_STATUSES),
                )
            ).first()
            if active is not None:
                raise ActiveJobError(project_id)
            session.add(
                JobRow(
                    id=job.id,
                    project_id=job.project_id,
                    kind=job.kind,
                    status=job.status,
                    error=job.error,
                    created_at=job.created_at,
                    updated_at=job.updated_at,
                )
            )
            session.commit()
        return job

    def get(self, job_id: str) -> Job | None:
        with Session(self._engine) as session:
            row = session.get(JobRow, job_id)
            return _to_job(row) if row else None

    def set_status(self, job_id: str, status: JobStatus, error: str | None = None) -> Job:
        with Session(self._engine) as session:
            row = session.get(JobRow, job_id)
            if row is None:
                raise KeyError(job_id)
            row.status = status
            row.error = error
            row.updated_at = utcnow()
            session.add(row)
            session.commit()
            session.refresh(row)
            return _to_job(row)

    def request_cancel(self, job_id: str) -> None:
        with Session(self._engine) as session:
            row = session.get(JobRow, job_id)
            if row is None:
                raise KeyError(job_id)
            row.cancel_requested = True
            session.add(row)
            session.commit()

    def cancel_requested(self, job_id: str) -> bool:
        with Session(self._engine) as session:
            row = session.get(JobRow, job_id)
            return bool(row and row.cancel_requested)
