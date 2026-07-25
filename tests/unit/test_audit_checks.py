from pathlib import Path

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
    product_used: str = "psha",
    product_expected: str = "psha",
    logo_used: str = "lsha",
    logo_expected: str = "lsha",
) -> SceneAudit:
    background = Image.new("RGB", (768, 1344), (44, 40, 32))
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
        palette=["#FF3B00", "#2C2820"],
        required_text=required or [],
        forbidden_claims=forbidden or [],
        product_sha_expected=product_expected,
        product_sha_used=product_used,
        logo_sha_expected=logo_expected,
        logo_sha_used=logo_used,
    )


def test_clean_scene_passes_all_checks(tmp_path: Path) -> None:
    scene = build_scene(tmp_path, required=["Make every space your studio"])
    report = audit_scene(scene, APPROVED)
    assert [c.check_id for c in report.checks] == ["A01", "A02", "A03", "A04", "A05", "A06", "A07"]
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
