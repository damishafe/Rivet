import secrets
from datetime import UTC, datetime

from sqlalchemy.engine import Engine
from sqlmodel import Session, select

from rivet.domain.models import BrandDNA, Project, utcnow
from rivet.domain.states import ProjectStatus, assert_transition
from rivet.storage.records import ProjectRow


def _aware(dt: datetime) -> datetime:
    return dt if dt.tzinfo is not None else dt.replace(tzinfo=UTC)


def _to_row(project: Project) -> ProjectRow:
    return ProjectRow(
        id=project.id,
        name=project.name,
        status=project.status.value,
        campaign_seed=project.campaign_seed,
        created_at=project.created_at,
        updated_at=project.updated_at,
        active_version=project.active_version,
        brief=project.brief,
    )


def _to_project(row: ProjectRow) -> Project:
    return Project(
        id=row.id,
        name=row.name,
        status=ProjectStatus(row.status),
        campaign_seed=row.campaign_seed,
        created_at=_aware(row.created_at),
        updated_at=_aware(row.updated_at),
        active_version=row.active_version,
        brief=row.brief,
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

    def set_brief(self, project_id: str, text: str) -> Project:
        with Session(self._engine) as session:
            row = session.get(ProjectRow, project_id)
            if row is None:
                raise KeyError(project_id)
            row.brief = text.strip()
            row.updated_at = utcnow()
            session.add(row)
            session.commit()
            session.refresh(row)
            return _to_project(row)

    def set_brand_dna(self, project_id: str, dna: BrandDNA) -> Project:
        with Session(self._engine) as session:
            row = session.get(ProjectRow, project_id)
            if row is None:
                raise KeyError(project_id)
            row.brand_dna = dna.model_dump(mode="json")
            if dna.confirmed_at is not None and row.status == ProjectStatus.DRAFT.value:
                assert_transition(ProjectStatus(row.status), ProjectStatus.BRAND_READY)
                row.status = ProjectStatus.BRAND_READY.value
            row.updated_at = utcnow()
            session.add(row)
            session.commit()
            session.refresh(row)
            return _to_project(row)

    def get_brand_dna(self, project_id: str) -> BrandDNA | None:
        with Session(self._engine) as session:
            row = session.get(ProjectRow, project_id)
            if row is None:
                raise KeyError(project_id)
            return BrandDNA.model_validate(row.brand_dna) if row.brand_dna else None
