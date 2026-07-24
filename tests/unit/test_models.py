import pytest
from pydantic import ValidationError

from rivet.domain.models import (
    BrandDNA,
    LogoPlacement,
    Motion,
    PaletteColor,
    PlanValidationError,
    ProductPlacement,
    Project,
    ShotCopy,
    ShotPlan,
    validate_plan,
)
from rivet.domain.states import ProjectStatus


def make_shot(shot_id: str, duration: float) -> ShotPlan:
    return ShotPlan(
        shot_id=shot_id,
        purpose="test",
        duration_s=duration,
        background_prompt="a stage",
        copy=ShotCopy(headline="H", support="S", cta="C"),
        product=ProductPlacement(anchor="center", scale=0.5, min_visible_area=0.2),
        logo=LogoPlacement(anchor="top_right", scale=0.1),
        layout_template="center_hero",
        motion=Motion(mode="controlled", camera="pan", intensity=0.3),
        narration="hello",
        seed=7,
    )


def test_project_defaults() -> None:
    project = Project(name="Kora Arc Launch", campaign_seed=42)
    assert project.status is ProjectStatus.DRAFT
    assert project.active_version == 1
    assert len(project.id) == 32


def test_palette_rejects_bad_hex() -> None:
    with pytest.raises(ValidationError):
        PaletteColor(hex="orange", role="primary")


def test_brand_dna_round_trips() -> None:
    dna = BrandDNA(
        product_name="Kora Arc",
        palette=[PaletteColor(hex="#FF3B00", role="primary")],
        tone=["bold"],
        audience="campus creators",
        required_text=["Make every space your studio"],
        forbidden_claims=["waterproof"],
        logo_asset_id="a" * 32,
        product_asset_id="b" * 32,
    )
    assert BrandDNA.model_validate(dna.model_dump()) == dna


def test_validate_plan_accepts_three_shots_in_window() -> None:
    validate_plan([make_shot("hook", 4), make_shot("proof", 5), make_shot("cta", 4)])


def test_validate_plan_rejects_wrong_order() -> None:
    with pytest.raises(PlanValidationError):
        validate_plan([make_shot("proof", 4), make_shot("hook", 5), make_shot("cta", 4)])


def test_validate_plan_rejects_duration_outside_window() -> None:
    with pytest.raises(PlanValidationError):
        validate_plan([make_shot("hook", 2), make_shot("proof", 2), make_shot("cta", 2)])


def test_shot_rejects_unknown_id() -> None:
    with pytest.raises(ValidationError):
        make_shot("outro", 4)
