import pytest
from sqlalchemy.engine import Engine

from rivet.adapters.heuristic_planner import propose_shots
from rivet.domain.models import (
    BrandDNA,
    PaletteColor,
    PlanValidationError,
    ShotCopy,
)
from rivet.domain.states import ProjectStatus
from rivet.storage.plans import PlanStore
from rivet.storage.projects import ProjectStore


def dna() -> BrandDNA:
    return BrandDNA(
        product_name="Kora Arc",
        palette=[PaletteColor(hex="#FF3B00", role="primary")],
        tone=["bold"],
        audience="campus creators",
        required_text=["Make every space your studio"],
        forbidden_claims=[],
        logo_asset_id="a" * 32,
        product_asset_id="b" * 32,
    )


def brand_ready_project(engine: Engine) -> str:
    projects = ProjectStore(engine)
    project = projects.create("Kora Arc", campaign_seed=42)
    projects.advance(project.id, ProjectStatus.BRAND_READY)
    return project.id


def test_set_plan_persists_and_advances(engine: Engine) -> None:
    project_id = brand_ready_project(engine)
    PlanStore(engine).set_plan(project_id, propose_shots(dna(), 42))
    stored = PlanStore(engine).get_plan(project_id)
    assert stored is not None and [s.shot_id for s in stored] == ["hook", "proof", "cta"]
    project = ProjectStore(engine).get(project_id)
    assert project is not None and project.status is ProjectStatus.PLANNED


def test_set_invalid_plan_rejected(engine: Engine) -> None:
    project_id = brand_ready_project(engine)
    shots = propose_shots(dna(), 42)
    shots[0].duration_s = 40
    with pytest.raises(PlanValidationError):
        PlanStore(engine).set_plan(project_id, shots)


def test_get_plan_none_when_unset(engine: Engine) -> None:
    project_id = brand_ready_project(engine)
    assert PlanStore(engine).get_plan(project_id) is None


def test_update_shot_replaces_and_revalidates(engine: Engine) -> None:
    project_id = brand_ready_project(engine)
    store = PlanStore(engine)
    store.set_plan(project_id, propose_shots(dna(), 42))
    plan = store.get_plan(project_id)
    assert plan is not None
    edited = plan[0].model_copy(update={"copy_": ShotCopy(headline="New", support="s", cta="c")})
    updated = store.update_shot(project_id, edited)
    assert updated[0].copy_.headline == "New"
    assert ProjectStore(engine).get(project_id).status is ProjectStatus.PLANNED  # type: ignore[union-attr]


def test_update_shot_that_breaks_window_rejected(engine: Engine) -> None:
    project_id = brand_ready_project(engine)
    store = PlanStore(engine)
    store.set_plan(project_id, propose_shots(dna(), 42))
    plan = store.get_plan(project_id)
    assert plan is not None
    broken = plan[0].model_copy(update={"duration_s": 40.0})
    with pytest.raises(PlanValidationError):
        store.update_shot(project_id, broken)


def test_update_unknown_shot_raises_lookup(engine: Engine) -> None:
    project_id = brand_ready_project(engine)
    store = PlanStore(engine)
    store.set_plan(project_id, propose_shots(dna(), 42))
    plan = store.get_plan(project_id)
    assert plan is not None
    orphan = plan[0].model_copy(update={"shot_id": "hook"})
    store.set_plan(project_id, propose_shots(dna(), 42))
    with pytest.raises(LookupError):
        store.update_shot("missing-project", orphan)
