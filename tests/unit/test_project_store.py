import pytest
from sqlalchemy.engine import Engine

from rivet.domain.states import InvalidTransition, ProjectStatus
from rivet.storage.projects import ProjectStore


def test_create_and_get_round_trip(engine: Engine) -> None:
    store = ProjectStore(engine)
    created = store.create("Kora Arc Launch")
    fetched = store.get(created.id)
    assert fetched == created
    assert fetched is not None
    assert fetched.status is ProjectStatus.DRAFT


def test_create_with_explicit_seed(engine: Engine) -> None:
    store = ProjectStore(engine)
    project = store.create("Seeded", campaign_seed=1234)
    assert project.campaign_seed == 1234


def test_get_unknown_returns_none(engine: Engine) -> None:
    assert ProjectStore(engine).get("missing") is None


def test_advance_moves_status_and_bumps_updated_at(engine: Engine) -> None:
    store = ProjectStore(engine)
    project = store.create("Advancing")
    advanced = store.advance(project.id, ProjectStatus.BRAND_READY)
    assert advanced.status is ProjectStatus.BRAND_READY
    assert advanced.updated_at >= project.updated_at


def test_advance_rejects_illegal_transition(engine: Engine) -> None:
    store = ProjectStore(engine)
    project = store.create("Illegal")
    with pytest.raises(InvalidTransition):
        store.advance(project.id, ProjectStatus.EXPORTED)


def test_advance_unknown_project_raises_key_error(engine: Engine) -> None:
    with pytest.raises(KeyError):
        ProjectStore(engine).advance("missing", ProjectStatus.BRAND_READY)


def test_list_all_returns_created_projects(engine: Engine) -> None:
    store = ProjectStore(engine)
    a = store.create("A")
    b = store.create("B")
    assert {p.id for p in store.list_all()} == {a.id, b.id}
