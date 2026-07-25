import hashlib
from pathlib import Path

from rivet.audit.checks import SceneAudit, audit_scene
from rivet.domain.layouts import LayoutTemplate, is_layout
from rivet.domain.models import BrandDNA, ShotPlan
from rivet.domain.receipt import CampaignReceipt, SceneResult


def _sha256(path: str) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def build_campaign_receipt(
    project_id: str,
    shots: list[ShotPlan],
    workdir: Path,
    brand: BrandDNA,
    logo_path: str,
    cutout_path: str,
    video_path: str | None = None,
    captions_path: str | None = None,
) -> CampaignReceipt:
    product_sha = _sha256(cutout_path)
    logo_sha = _sha256(logo_path)
    palette = [color.hex for color in brand.palette]
    scenes: list[SceneResult] = []
    for shot in shots:
        layout: LayoutTemplate = shot.layout_template if is_layout(shot.layout_template) else "center_hero"
        still_path = str(workdir / f"{shot.shot_id}-still.png")
        approved = {
            "headline": shot.copy_.headline,
            "support": shot.copy_.support,
            "cta": shot.copy_.cta,
        }
        scene = SceneAudit(
            layout=layout,
            still_path=still_path,
            cutout_path=cutout_path,
            logo_path=logo_path,
            headline=shot.copy_.headline,
            support=shot.copy_.support,
            cta=shot.copy_.cta,
            palette=palette,
            required_text=brand.required_text,
            forbidden_claims=brand.forbidden_claims,
            product_sha_expected=product_sha,
            product_sha_used=product_sha,
            logo_sha_expected=logo_sha,
            logo_sha_used=logo_sha,
        )
        report = audit_scene(scene, approved)
        scenes.append(
            SceneResult(
                shot_id=shot.shot_id,
                still_path=still_path,
                seed=shot.seed,
                checks=report.checks,
                passed=report.passed,
            )
        )
    receipt = CampaignReceipt(
        project_id=project_id,
        product_sha256=product_sha,
        logo_sha256=logo_sha,
        scenes=scenes,
        video_path=video_path,
        captions_path=captions_path,
        passed=all(scene.passed for scene in scenes),
    )
    return receipt.finalize()
