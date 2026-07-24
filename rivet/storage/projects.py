import secrets
from datetime import UTC

from sqlalchemy.engine import Engine
from sqlmodel import Session, select

from rivet.domain.models import Project, utcnow
from rivet.domain.states import ProjectStatus, assert_transition
from rivet.storage.records import ProjectRow


def _to_row(project: Project) -> ProjectRow:
    return ProjectRow(
        id=project.id,
        name=project.name,
        status=project.status.value,
        campaign_seed=project.campaign_seed,
        created_at=project.created_at,
        updated_at=project.updated_at,
        active_version=project.active_version,
    )


def _to_project(row: ProjectRow) -> Project:
    return Project(
        id=row.id,
        name=row.name,
        status=ProjectStatus(row.status),
        campaign_seed=row.campaign_seed,
        created_at=row.created_at.replace(tzinfo=UTC) if row.created_at.tzinfo is None else row.created_at,
        updated_at=row.updated_at.replace(tzinfo=UTC) if row.updated_at.tzinfo is None else row.updated_at,
        active_version=row.active_version,
    )


class ProjectStore:
    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def create(self, name: str, campaign_seed: int | None = None) -> Project:
        seed = campaign_seed if campaign_seed is not None else secrets.randbelow(2**31)
        project = Project(name=name, campaign_seed=seed)
        with Session(self._engine) as session:
            session.add(_to_row(project))
            session.commit()
        return project

    def get(self, project_id: str) -> Project | None:
        with Session(self._engine) as session:
            row = session.get(ProjectRow, project_id)
            return _to_project(row) if row else None

    def list_all(self) -> list[Project]:
        with Session(self._engine) as session:
            rows = session.exec(select(ProjectRow)).all()
            return [_to_project(row) for row in rows]

    def advance(self, project_id: str, target: ProjectStatus) -> Project:
        with Session(self._engine) as session:
            row = session.get(ProjectRow, project_id)
            if row is None:
                raise KeyError(project_id)
            assert_transition(ProjectStatus(row.status), target)
            row.status = target.value
            row.updated_at = utcnow()
            session.add(row)
            session.commit()
            session.refresh(row)
            return _to_project(row)
