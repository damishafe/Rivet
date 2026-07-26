from dataclasses import dataclass, field

from rivet.audit.scene import SceneAudit, mentions
from rivet.audit.semantic import SemanticJudge, check_semantic
from rivet.audit.visual_checks import (
    check_logo_presence,
    check_palette,
    check_product_fidelity,
    check_prominence,
    check_safe_area,
)
from rivet.domain.models import AuditCheck

__all__ = [
    "AuditReport",
    "SceneAudit",
    "audit_scene",
    "check_claims",
    "check_lineage",
    "check_logo_presence",
    "check_palette",
    "check_product_fidelity",
    "check_prominence",
    "check_safe_area",
    "check_text_integrity",
]


def check_lineage(scene: SceneAudit) -> AuditCheck:
    ok = (
        scene.product_sha_expected == scene.product_sha_used
        and scene.logo_sha_expected == scene.logo_sha_used
    )
    return AuditCheck(
        check_id="A01",
        metric="protected asset lineage",
        threshold="exact sha256 match",
        observed="match" if ok else "mismatch",
        passed=ok,
        owner_stage="compose",
    )


def check_text_integrity(scene: SceneAudit, approved: dict[str, str]) -> AuditCheck:
    rendered = {"headline": scene.headline, "support": scene.support, "cta": scene.cta}
    ok = rendered == approved
    return AuditCheck(
        check_id="A03",
        metric="rendered copy equals approved copy",
        threshold="exact string match",
        observed="match" if ok else "mismatch",
        passed=ok,
        owner_stage="copy/layout",
    )


def check_claims(scene: SceneAudit) -> AuditCheck:
    joined = f"{scene.headline} {scene.support} {scene.cta} {scene.narration}".lower()
    forbidden_hits = [f for f in scene.forbidden_claims if mentions(f, joined)]
    missing_required = [r for r in scene.required_text if not mentions(r, joined)]
    ok = not forbidden_hits and not missing_required
    detail = "clean" if ok else f"forbidden={forbidden_hits} missing={missing_required}"
    return AuditCheck(
        check_id="A07",
        metric="forbidden claims and required phrases",
        threshold="0 forbidden + all required",
        observed=detail,
        passed=ok,
        owner_stage="copy",
    )


@dataclass
class AuditReport:
    checks: list[AuditCheck] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return all(check.passed for check in self.checks if not check.advisory)


def audit_scene(
    scene: SceneAudit, approved_copy: dict[str, str], judge: SemanticJudge | None = None
) -> AuditReport:
    checks = [
        check_lineage(scene),
        check_logo_presence(scene),
        check_text_integrity(scene, approved_copy),
        check_palette(scene),
        check_safe_area(scene),
        check_prominence(scene),
        check_claims(scene),
        check_product_fidelity(scene),
    ]
    if judge is not None:
        message = f"{scene.headline} {scene.support} {scene.cta}".strip()
        checks.append(
            check_semantic(scene.still_path, scene.purpose, scene.audience, message, judge)
        )
    return AuditReport(checks=checks)
