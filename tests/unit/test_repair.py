from rivet.audit.repair import claims_failed, repair_copy
from rivet.domain.models import AuditCheck, ShotCopy


def _check(check_id: str, passed: bool) -> AuditCheck:
    return AuditCheck(
        check_id=check_id, metric="m", threshold="t", observed="o", passed=passed, owner_stage="s"
    )


def test_strips_forbidden_and_restores_required() -> None:
    copy = ShotCopy(headline="Kora Arc", support="The fully waterproof speaker", cta="Buy now")
    fixed = repair_copy(copy, ["waterproof"], ["Make every space your studio"])
    joined = f"{fixed.headline} {fixed.support} {fixed.cta}".lower()
    assert "waterproof" not in joined
    assert "make every space your studio" in joined


def test_forbidden_matching_is_word_bounded() -> None:
    copy = ShotCopy(headline="Waterproofing guide", support="s", cta="c")
    fixed = repair_copy(copy, ["water"], [])
    assert fixed.headline == "Waterproofing guide"


def test_claims_failed_detects_a07() -> None:
    assert claims_failed([_check("A07", False)])
    assert not claims_failed([_check("A07", True)])
    assert not claims_failed([_check("A04", False)])
