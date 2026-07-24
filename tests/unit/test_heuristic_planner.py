from rivet.adapters.heuristic_planner import propose_shots
from rivet.domain.models import BrandDNA, PaletteColor, validate_plan


def make_dna(required: list[str] | None = None) -> BrandDNA:
    return BrandDNA(
        product_name="Kora Arc",
        palette=[PaletteColor(hex="#FF3B00", role="primary")],
        tone=["bold", "energetic"],
        audience="campus creators",
        required_text=required if required is not None else ["Make every space your studio"],
        forbidden_claims=["waterproof"],
        logo_asset_id="a" * 32,
        product_asset_id="b" * 32,
    )


def test_produces_valid_three_shot_plan() -> None:
    shots = propose_shots(make_dna(), campaign_seed=42)
    assert [s.shot_id for s in shots] == ["hook", "proof", "cta"]
    validate_plan(shots)


def test_layouts_and_motion_assigned() -> None:
    shots = propose_shots(make_dna(), campaign_seed=42)
    assert [s.layout_template for s in shots] == ["center_hero", "split_proof", "cta_lockup"]
    assert shots[0].motion.mode == "i2v"
    assert shots[1].motion.mode == "controlled"
    assert shots[2].motion.mode == "controlled"


def test_cta_uses_required_text() -> None:
    shots = propose_shots(make_dna(["Make every space your studio"]), campaign_seed=42)
    assert shots[2].copy_.cta == "Make every space your studio"


def test_cta_falls_back_without_required_text() -> None:
    shots = propose_shots(make_dna([]), campaign_seed=42)
    assert shots[2].copy_.cta == "Discover Kora Arc"


def test_seeds_are_deterministic_and_distinct() -> None:
    first = propose_shots(make_dna(), campaign_seed=42)
    second = propose_shots(make_dna(), campaign_seed=42)
    assert [s.seed for s in first] == [s.seed for s in second]
    assert len({s.seed for s in first}) == 3
