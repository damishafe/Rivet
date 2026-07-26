from pathlib import Path

from PIL import Image, ImageDraw

from rivet.audit.receipt import build_campaign_receipt
from rivet.compositor.compose import compose_still
from rivet.domain.models import (
    BrandDNA,
    LogoPlacement,
    Motion,
    PaletteColor,
    ProductPlacement,
    ShotCopy,
    ShotPlan,
)

ACCENT = (255, 59, 0)


def make_shot(shot_id: str, support: str = "Make every space your studio", cta: str = "Shop now") -> ShotPlan:
    return ShotPlan(
        shot_id=shot_id,
        purpose="p",
        duration_s=4,
        background_prompt="bg",
        copy=ShotCopy(headline="Kora Arc", support=support, cta=cta),
        product=ProductPlacement(anchor="center", scale=0.5, min_visible_area=0.2),
        logo=LogoPlacement(anchor="top_right", scale=0.1),
        layout_template="center_hero",
        motion=Motion(mode="controlled", camera="pan", intensity=0.3),
        narration="n",
        seed=7,
    )


def make_brand(forbidden: list[str] | None = None, required: list[str] | None = None) -> BrandDNA:
    return BrandDNA(
        product_name="Kora Arc",
        palette=[PaletteColor(hex="#FF3B00", role="primary"), PaletteColor(hex="#2C2820", role="bg")],
        tone=["bold"],
        audience="campus creators",
        required_text=required if required is not None else ["Make every space your studio"],
        forbidden_claims=forbidden or [],
        logo_asset_id="a" * 32,
        product_asset_id="b" * 32,
    )


def setup_scene(tmp_path: Path, shots: list[ShotPlan]) -> tuple[Path, str, str, dict[str, str]]:
    workdir = tmp_path / "work"
    workdir.mkdir()
    background = Image.new("RGB", (768, 1344), (44, 40, 32))
    bg_path = tmp_path / "bg.png"
    background.save(bg_path)
    cutout = Image.new("RGBA", (400, 500), (0, 0, 0, 0))
    ImageDraw.Draw(cutout).rounded_rectangle([40, 40, 360, 460], radius=40, fill=(40, 40, 44, 255))
    cutout_path = tmp_path / "cutout.png"
    cutout.save(cutout_path)
    logo = Image.new("RGBA", (200, 60), (250, 250, 250, 255))
    logo_path = tmp_path / "logo.png"
    logo.save(logo_path)
    for shot in shots:
        still = compose_still(
            background, cutout, logo, shot.copy_.headline, shot.copy_.support, shot.copy_.cta,
            "center_hero", ACCENT,
        )
        still.save(workdir / f"{shot.shot_id}-still.png")
    backgrounds = {shot.shot_id: str(bg_path) for shot in shots}
    return workdir, str(logo_path), str(cutout_path), backgrounds


def test_clean_campaign_receipt_passes(tmp_path: Path) -> None:
    shots = [make_shot("hook"), make_shot("proof"), make_shot("cta")]
    workdir, logo_path, cutout_path, backgrounds = setup_scene(tmp_path, shots)
    receipt = build_campaign_receipt(
        "proj1", shots, workdir, make_brand(), logo_path, cutout_path, backgrounds, ACCENT
    )
    assert receipt.passed
    assert receipt.repairs == []
    assert [s.shot_id for s in receipt.scenes] == ["hook", "proof", "cta"]
    assert all(len(s.checks) == 9 for s in receipt.scenes)
    assert len(receipt.receipt_hash) == 64


def test_forbidden_claim_gets_repaired(tmp_path: Path) -> None:
    shots = [make_shot("hook", support="The fully waterproof speaker")]
    workdir, logo_path, cutout_path, backgrounds = setup_scene(tmp_path, shots)
    brand = make_brand(forbidden=["waterproof"], required=["Make every space your studio"])
    receipt = build_campaign_receipt(
        "proj1", shots, workdir, brand, logo_path, cutout_path, backgrounds, ACCENT
    )
    assert receipt.passed
    assert len(receipt.repairs) == 1
    repair = receipt.repairs[0]
    assert repair.shot_id == "hook"
    assert repair.before_passed is False
    assert repair.after_passed is True
    a07 = next(c for c in receipt.scenes[0].checks if c.check_id == "A07")
    assert a07.passed


def test_receipt_hash_is_stable(tmp_path: Path) -> None:
    shots = [make_shot("hook")]
    workdir, logo_path, cutout_path, backgrounds = setup_scene(tmp_path, shots)
    first = build_campaign_receipt(
        "proj1", shots, workdir, make_brand(), logo_path, cutout_path, backgrounds, ACCENT
    )
    second = build_campaign_receipt(
        "proj1", shots, workdir, make_brand(), logo_path, cutout_path, backgrounds, ACCENT
    )
    assert first.receipt_hash == second.receipt_hash
