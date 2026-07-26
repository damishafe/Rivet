from pathlib import Path

from PIL import Image

from rivet.audit.checks import SceneAudit, audit_scene
from rivet.audit.semantic import check_semantic


def high_judge(image_path: str, question: str) -> tuple[int, str]:
    return 90, "Great fit"


def low_judge(image_path: str, question: str) -> tuple[int, str]:
    return 40, "Weak fit"


def test_check_semantic_passes_above_threshold(tmp_path: Path) -> None:
    still = tmp_path / "s.png"
    Image.new("RGB", (10, 10), (0, 0, 0)).save(still)
    check = check_semantic(str(still), "hook", "campus creators", "Kora Arc", high_judge)
    assert check.check_id == "A08"
    assert check.passed
    assert check.advisory
    assert str(check.observed).startswith("90")


def raising_judge(image_path: str, question: str) -> tuple[int, str]:
    raise RuntimeError("weights missing")


def test_check_semantic_survives_judge_failure(tmp_path: Path) -> None:
    still = tmp_path / "s.png"
    Image.new("RGB", (10, 10), (0, 0, 0)).save(still)
    check = check_semantic(str(still), "hook", "campus creators", "Kora Arc", raising_judge)
    assert check.check_id == "A08"
    assert not check.passed
    assert check.advisory
    assert "judge unavailable" in str(check.observed)


def make_scene(tmp_path: Path) -> SceneAudit:
    still = tmp_path / "still.png"
    Image.new("RGB", (10, 10), (0, 0, 0)).save(still)
    return SceneAudit(
        layout="center_hero", still_path=str(still), cutout_path=str(still), logo_path=str(still),
        headline="Kora Arc", support="s", cta="c", palette=["#FF3B00"], required_text=[],
        forbidden_claims=[], product_sha_expected="a", product_sha_used="a",
        logo_sha_expected="b", logo_sha_used="b", purpose="hook", audience="campus creators",
    )


def test_advisory_semantic_does_not_fail_report(tmp_path: Path) -> None:
    scene = make_scene(tmp_path)
    approved = {"headline": "Kora Arc", "support": "s", "cta": "c"}
    report = audit_scene(scene, approved, low_judge)
    a08 = next(c for c in report.checks if c.check_id == "A08")
    assert not a08.passed
    deterministic_pass = all(c.passed for c in report.checks if not c.advisory)
    assert report.passed == deterministic_pass


def test_audit_scene_without_judge_has_only_deterministic_checks(tmp_path: Path) -> None:
    scene = make_scene(tmp_path)
    report = audit_scene(scene, {"headline": "Kora Arc", "support": "s", "cta": "c"})
    assert len(report.checks) == 8
    assert not any(c.check_id == "A08" for c in report.checks)
    assert not any(c.advisory for c in report.checks)
