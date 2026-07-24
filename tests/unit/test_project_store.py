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


def test_set_brief_strips_and_persists(engine: Engine) -> None:
    store = ProjectStore(engine)
    project = store.create("Briefed")
    updated = store.set_brief(project.id, "  Launch the Kora Arc speaker to campus creators.  ")
    assert updated.brief == "Launch the Kora Arc speaker to campus creators."
    fetched = store.get(project.id)
    assert fetched is not None and fetched.brief == updated.brief


def test_set_brief_unknown_project_raises(engine: Engine) -> None:
    with pytest.raises(KeyError):
        ProjectStore(engine).set_brief("missing", "x" * 40)


from rivet.domain.models import BrandDNA, PaletteColor, utcnow


def make_dna(confirmed: bool = False) -> BrandDNA:
    return BrandDNA(
        product_name="Kora Arc",
        palette=[PaletteColor(hex="#FF3B00", role="primary")],
        tone=["bold"],
        audience="campus creators",
        required_text=["Make every space your studio"],
        forbidden_claims=["waterproof"],
        logo_asset_id="a" * 32,
        product_asset_id="b" * 32,
        confirmed_at=utcnow() if confirmed else None,
    )


def test_brand_dna_round_trips_unconfirmed(engine: Engine) -> None:
    store = ProjectStore(engine)
    project = store.create("DNA")
    store.set_brand_dna(project.id, make_dna())
    fetched = store.get_brand_dna(project.id)
    assert fetched is not None and fetched.product_name == "Kora Arc"
    refreshed = store.get(project.id)
    assert refreshed is not None and refreshed.status is ProjectStatus.DRAFT


def test_confirmed_dna_advances_to_brand_ready(engine: Engine) -> None:
    store = ProjectStore(engine)
    project = store.create("DNA2")
    updated = store.set_brand_dna(project.id, make_dna(confirmed=True))
    assert updated.status is ProjectStatus.BRAND_READY


def test_reconfirming_when_already_brand_ready_keeps_status(engine: Engine) -> None:
    store = ProjectStore(engine)
    project = store.create("DNA3")
    store.set_brand_dna(project.id, make_dna(confirmed=True))
    updated = store.set_brand_dna(project.id, make_dna(confirmed=True))
    assert updated.status is ProjectStatus.BRAND_READY


def test_get_brand_dna_missing_returns_none(engine: Engine) -> None:
    store = ProjectStore(engine)
    project = store.create("Empty")
    assert store.get_brand_dna(project.id) is None
