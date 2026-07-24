from sqlalchemy.engine import Engine
from sqlmodel import Session

from rivet.domain.models import ShotPlan, utcnow, validate_plan
from rivet.domain.states import ProjectStatus, assert_transition
from rivet.storage.records import ProjectRow


class PlanStore:
    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def set_plan(self, project_id: str, shots: list[ShotPlan]) -> None:
        validate_plan(shots)
        with Session(self._engine) as session:
            row = session.get(ProjectRow, project_id)
            if row is None:
                raise KeyError(project_id)
            row.shots = [shot.model_dump(mode="json") for shot in shots]
            if row.status == ProjectStatus.BRAND_READY.value:
                assert_transition(ProjectStatus(row.status), ProjectStatus.PLANNED)
                row.status = ProjectStatus.PLANNED.value
            row.updated_at = utcnow()
            session.add(row)
            session.commit()

    def get_plan(self, project_id: str) -> list[ShotPlan] | None:
        with Session(self._engine) as session:
            row = session.get(ProjectRow, project_id)
            if row is None:
                raise KeyError(project_id)
            if row.shots is None:
                return None
            return [ShotPlan.model_validate(shot) for shot in row.shots]

    def update_shot(self, project_id: str, shot: ShotPlan) -> list[ShotPlan]:
        current = self.get_plan(project_id)
        if current is None:
            raise LookupError("no plan to update")
        if shot.shot_id not in {existing.shot_id for existing in current}:
            raise LookupError(f"shot {shot.shot_id} not in plan")
        updated = [shot if existing.shot_id == shot.shot_id else existing for existing in current]
        self.set_plan(project_id, updated)
        return updated
