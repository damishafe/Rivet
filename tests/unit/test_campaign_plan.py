from pathlib import Path

from rivet.domain.models import (
    Asset,
    BrandDNA,
    LogoPlacement,
    Motion,
    PaletteColor,
    ProductPlacement,
    Project,
    ShotCopy,
    ShotPlan,
)
from rivet.pipeline.campaign_inputs import (
    CampaignInputs,
    CampaignStages,
    generation_plan,
    render_plan,
)

LANGUAGE_BEARING = ("composite", "narration")


def make_inputs(language: str) -> CampaignInputs:
    brand = BrandDNA(
        product_name="Kora Arc",
        palette=[PaletteColor(hex="#FF3B00", role="primary")],
        tone=["bold"],
        audience="campus creators",
        required_text=[],
        forbidden_claims=[],
        logo_asset_id="a" * 32,
        product_asset_id="b" * 32,
        language=language,
    )
    shot = ShotPlan(
        shot_id="hook",
        purpose="test",
        duration_s=4.0,
        background_prompt="a stage",
        copy=ShotCopy(headline="H", support="S", cta="C"),
        product=ProductPlacement(anchor="center", scale=0.5, min_visible_area=0.2),
        logo=LogoPlacement(anchor="top_right", scale=0.1),
        layout_template="center_hero",
        motion=Motion(mode="controlled", camera="pan", intensity=0.3),
        narration="hello",
        seed=7,
    )
    asset = Asset(
        project_id="p" * 32, role="product", path="product.png",
        sha256="c" * 64, mime="image/png",
    )
    return CampaignInputs(
        project=Project(name="Kora Arc", campaign_seed=42),
        shots=[shot],
        brand=brand,
        product=asset,
        logo=asset.model_copy(update={"role": "logo"}),
    )


def language_configs(language: str) -> dict[str, str | None]:
    inputs = make_inputs(language)
    stages = CampaignStages()
    workdir = Path("work")
    planned = generation_plan(inputs, stages, workdir, (255, 59, 0))
    planned += render_plan(inputs, stages, workdir)
    return {
        step.request.stage.split(".")[0]: step.request.config.get("language")
        for step in planned
        if step.request.stage.split(".")[0] in LANGUAGE_BEARING
    }


def test_every_language_bearing_stage_is_told_the_language() -> None:
    """The compositor picks its font from this: without it, Chinese is drawn with Inter."""
    assert language_configs("zh") == {"composite": "zh", "narration": "zh"}


def test_language_reaches_stages_for_the_default_too() -> None:
    assert language_configs("en") == {"composite": "en", "narration": "en"}
