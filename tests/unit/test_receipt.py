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


def make_shot(shot_id: str, cta: str = "Shop now") -> ShotPlan:
    return ShotPlan(
        shot_id=shot_id,
        purpose="p",
        duration_s=4,
        background_prompt="bg",
        copy=ShotCopy(headline="Kora Arc", support="Make every space your studio", cta=cta),
        product=ProductPlacement(anchor="center", scale=0.5, min_visible_area=0.2),
        logo=LogoPlacement(anchor="top_right", scale=0.1),
        layout_template="center_hero",
        motion=Motion(mode="controlled", camera="pan", intensity=0.3),
        narration="n",
        seed=7,
    )


def make_brand(forbidden: list[str] | None = None) -> BrandDNA:
    return BrandDNA(
        product_name="Kora Arc",
        palette=[PaletteColor(hex="#FF3B00", role="primary"), PaletteColor(hex="#2C2820", role="bg")],
        tone=["bold"],
        audience="campus creators",
        required_text=["Make every space your studio"],
        forbidden_claims=forbidden or [],
        logo_asset_id="a" * 32,
        product_asset_id="b" * 32,
    )


def setup_scene(tmp_path: Path, shots: list[ShotPlan]) -> tuple[Path, str, str]:
    workdir = tmp_path / "work"
    workdir.mkdir()
    background = Image.new("RGB", (768, 1344), (44, 40, 32))
    cutout = Image.new("RGBA", (400, 500), (0, 0, 0, 0))
    ImageDraw.Draw(cutout).rounded_rectangle([40, 40, 360, 460], radius=40, fill=(40, 40, 44, 255))
    logo = Image.new("RGBA", (200, 60), (250, 250, 250, 255))
    cutout_path = tmp_path / "cutout.png"
    cutout.save(cutout_path)
    logo_path = tmp_path / "logo.png"
    logo.save(logo_path)
    for shot in shots:
        still = compose_still(
            background, cutout, logo, shot.copy_.headline, shot.copy_.support, shot.copy_.cta,
            "center_hero", (255, 59, 0),
        )
        still.save(workdir / f"{shot.shot_id}-still.png")
    return workdir, str(logo_path), str(cutout_path)


def test_clean_campaign_receipt_passes(tmp_path: Path) -> None:
    shots = [make_shot("hook"), make_shot("proof"), make_shot("cta")]
    workdir, logo_path, cutout_path = setup_scene(tmp_path, shots)
    receipt = build_campaign_receipt("proj1", shots, workdir, make_brand(), logo_path, cutout_path)
    assert receipt.passed
    assert [s.shot_id for s in receipt.scenes] == ["hook", "proof", "cta"]
    assert all(len(s.checks) == 7 for s in receipt.scenes)
    assert len(receipt.receipt_hash) == 64


def test_forbidden_claim_fails_campaign(tmp_path: Path) -> None:
    shots = [make_shot("hook", cta="Now fully waterproof")]
    workdir, logo_path, cutout_path = setup_scene(tmp_path, shots)
    receipt = build_campaign_receipt(
        "proj1", shots, workdir, make_brand(forbidden=["waterproof"]), logo_path, cutout_path
    )
    assert not receipt.passed
    a07 = next(c for c in receipt.scenes[0].checks if c.check_id == "A07")
    assert not a07.passed


def test_receipt_hash_is_stable(tmp_path: Path) -> None:
    shots = [make_shot("hook")]
    workdir, logo_path, cutout_path = setup_scene(tmp_path, shots)
    first = build_campaign_receipt("proj1", shots, workdir, make_brand(), logo_path, cutout_path)
    second = build_campaign_receipt("proj1", shots, workdir, make_brand(), logo_path, cutout_path)
    assert first.receipt_hash == second.receipt_hash
