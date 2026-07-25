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
FIXTURE = Path(__file__).resolve().parents[2] / "fixtures" / "kora-arc"


def _shot(shot_id: str, layout: str) -> ShotPlan:
    return ShotPlan(
        shot_id=shot_id,
        purpose="hook the viewer",
        duration_s=4,
        background_prompt="warm studio desk",
        copy=ShotCopy(
            headline="Kora Arc", support="Make every space your studio", cta="Shop now"
        ),
        product=ProductPlacement(anchor="center", scale=0.5, min_visible_area=0.2),
        logo=LogoPlacement(anchor="top_right", scale=0.1),
        layout_template=layout,  # type: ignore[arg-type]
        motion=Motion(mode="controlled", camera="pan", intensity=0.3),
        narration="Kora Arc turns any corner into a studio.",
        seed=7,
    )


def _brand() -> BrandDNA:
    return BrandDNA(
        product_name="Kora Arc",
        palette=[
            PaletteColor(hex="#FF3B00", role="primary"),
            PaletteColor(hex="#2C2820", role="bg"),
        ],
        tone=["bold"],
        audience="campus creators",
        required_text=["Make every space your studio"],
        forbidden_claims=["waterproof"],
        logo_asset_id="a" * 32,
        product_asset_id="b" * 32,
    )


def _cutout(path: Path) -> None:
    cutout = Image.new("RGBA", (520, 640), (0, 0, 0, 0))
    ImageDraw.Draw(cutout).ellipse([60, 98, 460, 542], fill=(40, 40, 44, 255))
    cutout.save(path)


def test_compositor_is_byte_reproducible(tmp_path: Path) -> None:
    background = Image.open(FIXTURE / "product.png").convert("RGB").resize((768, 1344))
    cutout_path = tmp_path / "cutout.png"
    _cutout(cutout_path)
    cutout = Image.open(cutout_path).convert("RGBA")
    logo = Image.open(FIXTURE / "logo.png").convert("RGBA")

    renders = []
    for index in range(2):
        still = compose_still(
            background, cutout, logo, "Kora Arc", "Make every space your studio",
            "Shop now", "center_hero", ACCENT,
        )
        out = tmp_path / f"still-{index}.png"
        still.save(out)
        renders.append(out.read_bytes())
    assert renders[0] == renders[1], "identical inputs must composite to identical bytes"


def test_receipt_hash_is_reproducible_across_layouts(tmp_path: Path) -> None:
    workdir = tmp_path / "work"
    workdir.mkdir()
    cutout_path = tmp_path / "cutout.png"
    _cutout(cutout_path)
    background = Image.new("RGB", (768, 1344), (44, 40, 32))
    cutout = Image.open(cutout_path).convert("RGBA")
    logo = Image.open(FIXTURE / "logo.png").convert("RGBA")

    shots = [
        _shot("hook", "center_hero"),
        _shot("proof", "split_proof"),
        _shot("cta", "cta_lockup"),
    ]
    backgrounds: dict[str, str] = {}
    for shot in shots:
        bg_path = tmp_path / f"{shot.shot_id}-bg.png"
        background.save(bg_path)
        backgrounds[shot.shot_id] = str(bg_path)
        still = compose_still(
            background, cutout, logo, shot.copy_.headline, shot.copy_.support,
            shot.copy_.cta, shot.layout_template, ACCENT,
        )
        still.save(workdir / f"{shot.shot_id}-still.png")

    hashes = []
    for _ in range(2):
        receipt = build_campaign_receipt(
            "golden", shots, workdir, _brand(), str(FIXTURE / "logo.png"),
            str(cutout_path), backgrounds, ACCENT,
        )
        assert receipt.passed, [
            (s.shot_id, c.check_id, c.observed)
            for s in receipt.scenes
            for c in s.checks
            if not c.passed
        ]
        hashes.append(receipt.receipt_hash)
    assert hashes[0] == hashes[1], "same inputs must yield the same receipt hash"
    assert len(hashes[0]) == 64
