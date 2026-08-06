from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from rivet.audit.checks import SceneAudit, audit_scene, check_palette, check_prominence
from rivet.compositor.compose import compose_still
from rivet.compositor.geometry import GEOMETRY, rect_px
from rivet.domain.models import AuditCheck

APPROVED = {"headline": "Kora Arc", "support": "Make every space your studio", "cta": "Shop now"}


def build_scene(
    tmp_path: Path,
    *,
    headline: str = "Kora Arc",
    support: str = "Make every space your studio",
    cta: str = "Shop now",
    forbidden: list[str] | None = None,
    required: list[str] | None = None,
    narration: str = "",
    palette: list[str] | None = None,
    bg_color: tuple[int, int, int] = (44, 40, 32),
    product_used: str = "psha",
    product_expected: str = "psha",
    logo_used: str = "lsha",
    logo_expected: str = "lsha",
) -> SceneAudit:
    background = Image.new("RGB", (768, 1344), bg_color)
    bg_path = tmp_path / "bg.png"
    background.save(bg_path)
    cutout = Image.new("RGBA", (400, 500), (0, 0, 0, 0))
    ImageDraw.Draw(cutout).rounded_rectangle([40, 40, 360, 460], radius=40, fill=(40, 40, 44, 255))
    cut_path = tmp_path / "cut.png"
    cutout.save(cut_path)
    logo = Image.new("RGBA", (200, 60), (250, 250, 250, 255))
    logo_path = tmp_path / "logo.png"
    logo.save(logo_path)
    still = compose_still(background, cutout, logo, headline, support, cta, "center_hero", (255, 59, 0))
    still_path = tmp_path / "still.png"
    still.save(still_path)
    return SceneAudit(
        layout="center_hero",
        still_path=str(still_path),
        cutout_path=str(cut_path),
        logo_path=str(logo_path),
        headline=headline,
        support=support,
        cta=cta,
        palette=palette or ["#FF3B00", "#2C2820"],
        required_text=required or [],
        forbidden_claims=forbidden or [],
        narration=narration,
        product_sha_expected=product_expected,
        product_sha_used=product_used,
        logo_sha_expected=logo_expected,
        logo_sha_used=logo_used,
    )


def test_clean_scene_passes_all_checks(tmp_path: Path) -> None:
    scene = build_scene(tmp_path, required=["Make every space your studio"])
    report = audit_scene(scene, APPROVED)
    assert [c.check_id for c in report.checks] == [
        "A01", "A02", "A03", "A04", "A05", "A06", "A07", "A09", "A10", "A11",
    ]
    assert report.passed, [(c.check_id, c.observed) for c in report.checks if not c.passed]


def test_forbidden_claim_fails_a07(tmp_path: Path) -> None:
    scene = build_scene(
        tmp_path, support="The fully waterproof speaker", forbidden=["waterproof"]
    )
    report = audit_scene(scene, {**APPROVED, "support": "The fully waterproof speaker"})
    a07 = next(c for c in report.checks if c.check_id == "A07")
    assert not a07.passed
    assert not report.passed


def test_missing_required_phrase_fails_a07(tmp_path: Path) -> None:
    scene = build_scene(tmp_path, support="Something else", required=["Make every space your studio"])
    report = audit_scene(scene, {**APPROVED, "support": "Something else"})
    assert not next(c for c in report.checks if c.check_id == "A07").passed


def test_text_mismatch_fails_a03(tmp_path: Path) -> None:
    scene = build_scene(tmp_path)
    report = audit_scene(scene, {**APPROVED, "headline": "Wrong Headline"})
    assert not next(c for c in report.checks if c.check_id == "A03").passed


def test_lineage_mismatch_fails_a01(tmp_path: Path) -> None:
    scene = build_scene(tmp_path, product_used="tampered", product_expected="original")
    report = audit_scene(scene, APPROVED)
    assert not next(c for c in report.checks if c.check_id == "A01").passed


def test_logo_overwritten_fails_a02(tmp_path: Path) -> None:
    scene = build_scene(tmp_path)
    still = Image.open(scene.still_path).convert("RGB")
    x, y, w, h = rect_px(GEOMETRY["center_hero"]["logo"], scene.canvas)
    ImageDraw.Draw(still).rectangle([x, y, x + w, y + h], fill=(0, 0, 0))
    still.save(scene.still_path)
    report = audit_scene(scene, APPROVED)
    a02 = next(c for c in report.checks if c.check_id == "A02")
    assert not a02.passed


def test_flat_frame_does_not_crash(tmp_path: Path) -> None:
    still_path = tmp_path / "flat.png"
    Image.new("RGB", (1080, 1920), (120, 120, 120)).save(still_path)
    scene = SceneAudit(
        layout="center_hero",
        still_path=str(still_path),
        cutout_path=str(still_path),
        logo_path=str(still_path),
        headline="",
        support="",
        cta="",
        palette=["#FF3B00", "#2C2820"],
        required_text=[],
        forbidden_claims=[],
        product_sha_expected="a",
        product_sha_used="a",
        logo_sha_expected="b",
        logo_sha_used="b",
    )
    check = check_palette(scene)
    assert isinstance(check, AuditCheck)


def test_thin_cutout_fails_a06(tmp_path: Path) -> None:
    scene = build_scene(tmp_path)
    thin_path = tmp_path / "thin_cut.png"
    Image.new("RGBA", (800, 20), (255, 90, 0, 255)).save(thin_path)
    scene.cutout_path = str(thin_path)
    a06 = check_prominence(scene)
    assert not a06.passed


def test_forbidden_claim_respects_word_boundary(tmp_path: Path) -> None:
    clean_scene = build_scene(tmp_path, support="Total freedom of movement", forbidden=["free"])
    clean_report = audit_scene(clean_scene, {**APPROVED, "support": "Total freedom of movement"})
    assert next(c for c in clean_report.checks if c.check_id == "A07").passed

    hit_scene = build_scene(tmp_path, support="Buy one, get one free", forbidden=["free"])
    hit_report = audit_scene(hit_scene, {**APPROVED, "support": "Buy one, get one free"})
    assert not next(c for c in hit_report.checks if c.check_id == "A07").passed


def test_forbidden_claim_with_punctuation_edges_is_caught(tmp_path: Path) -> None:
    scene = build_scene(
        tmp_path, support="Satisfaction 100% guaranteed", forbidden=["100%", "#1"]
    )
    report = audit_scene(scene, {**APPROVED, "support": "Satisfaction 100% guaranteed"})
    a07 = next(c for c in report.checks if c.check_id == "A07")
    assert not a07.passed
    assert "100%" in str(a07.observed)


def test_forbidden_claim_in_narration_is_caught(tmp_path: Path) -> None:
    scene = build_scene(tmp_path, narration="Now fully waterproof for the beach", forbidden=["waterproof"])
    report = audit_scene(scene, APPROVED)
    assert not next(c for c in report.checks if c.check_id == "A07").passed


def test_required_phrase_requires_whole_word(tmp_path: Path) -> None:
    scene = build_scene(tmp_path, support="Total freedom of movement", required=["free"])
    report = audit_scene(scene, {**APPROVED, "support": "Total freedom of movement"})
    assert not next(c for c in report.checks if c.check_id == "A07").passed


def test_overflowing_headline_fails_a05(tmp_path: Path) -> None:
    huge = "Supercalifragilisticexpialidocious" * 6
    scene = build_scene(tmp_path, headline=huge)
    a05 = next(c for c in audit_scene(scene, APPROVED).checks if c.check_id == "A05")
    assert not a05.passed


def test_fitting_copy_passes_a05(tmp_path: Path) -> None:
    scene = build_scene(tmp_path)
    a05 = next(c for c in audit_scene(scene, APPROVED).checks if c.check_id == "A05")
    assert a05.passed


def test_every_layout_satisfies_prominence_policy(tmp_path: Path) -> None:
    scene = build_scene(tmp_path)
    cutout = Image.new("RGBA", (520, 640), (0, 0, 0, 0))
    ImageDraw.Draw(cutout).ellipse([60, 98, 460, 542], fill=(40, 40, 44, 255))
    cutout_path = tmp_path / "typical_product.png"
    cutout.save(cutout_path)
    coverage = float((np.asarray(Image.open(cutout_path))[:, :, 3] > 128).mean())
    assert 0.40 <= coverage <= 0.45, "cutout must model a real segmented product"
    scene.cutout_path = str(cutout_path)
    for layout in GEOMETRY:
        scene.layout = layout  # type: ignore[assignment]
        check = check_prominence(scene)
        assert check.passed, f"{layout} renders the product at {check.observed} of frame"


def test_repainted_product_fails_a09(tmp_path: Path) -> None:
    scene = build_scene(tmp_path)
    still = Image.open(scene.still_path).convert("RGB")
    x, y, w, h = rect_px(GEOMETRY["center_hero"]["product"], scene.canvas)
    ImageDraw.Draw(still).rectangle([x, y, x + w, y + h], fill=(255, 0, 0))
    still.save(scene.still_path)
    a09 = next(c for c in audit_scene(scene, APPROVED).checks if c.check_id == "A09")
    assert not a09.passed


def test_faithful_product_passes_a09(tmp_path: Path) -> None:
    scene = build_scene(tmp_path)
    a09 = next(c for c in audit_scene(scene, APPROVED).checks if c.check_id == "A09")
    assert a09.passed, a09.observed


def test_bright_background_still_renders_legible_text(tmp_path: Path) -> None:
    scene = build_scene(tmp_path, bg_color=(245, 245, 245))
    a10 = next(c for c in audit_scene(scene, APPROVED).checks if c.check_id == "A10")
    assert a10.passed, f"white studio background left text at {a10.observed}:1"


def test_washed_out_text_fails_a10(tmp_path: Path) -> None:
    scene = build_scene(tmp_path)
    still = Image.open(scene.still_path).convert("RGB")
    x, y, w, h = rect_px(GEOMETRY["center_hero"]["headline"], scene.canvas)
    ImageDraw.Draw(still).rectangle([x, y, x + w, y + h], fill=(252, 252, 252))
    still.save(scene.still_path)
    a10 = next(c for c in audit_scene(scene, APPROVED).checks if c.check_id == "A10")
    assert not a10.passed


def test_all_neutral_brand_flags_saturated_background(tmp_path: Path) -> None:
    scene = build_scene(
        tmp_path, palette=["#141414", "#EDEDED"], bg_color=(200, 30, 30)
    )
    assert not check_palette(scene).passed


def test_glyph_coverage_rejects_copy_the_font_cannot_draw(tmp_path: Path) -> None:
    """Chinese copy drawn with the Latin font renders as boxes; A11 is what notices."""
    scene = build_scene(tmp_path, headline="音质出众")
    unreadable = audit_scene(scene, {**APPROVED, "headline": "音质出众"})
    a11 = next(c for c in unreadable.checks if c.check_id == "A11")
    assert not a11.passed
    assert "音" in str(a11.observed)

    readable = build_scene(tmp_path, headline="音质出众")
    readable.font = "NotoSansSC.ttf"
    report = audit_scene(readable, {**APPROVED, "headline": "音质出众"})
    assert next(c for c in report.checks if c.check_id == "A11").passed


def test_glyph_coverage_passes_for_latin_copy(tmp_path: Path) -> None:
    scene = build_scene(tmp_path)
    report = audit_scene(scene, APPROVED)
    assert next(c for c in report.checks if c.check_id == "A11").passed
