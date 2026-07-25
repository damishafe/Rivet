import hashlib
from pathlib import Path

from PIL import Image

from rivet.audit.checks import SceneAudit, audit_scene
from rivet.audit.repair import claims_failed, repair_copy
from rivet.audit.semantic import SemanticJudge
from rivet.compositor.compose import compose_still
from rivet.domain.layouts import LayoutTemplate, is_layout
from rivet.domain.models import BrandDNA, ShotCopy, ShotPlan
from rivet.domain.receipt import CampaignReceipt, RepairRecord, SceneResult

Color = tuple[int, int, int]


def _sha256(path: str) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _recomposite(
    background_path: str,
    cutout_path: str,
    logo_path: str,
    copy: ShotCopy,
    layout: LayoutTemplate,
    accent: Color,
    still_path: str,
) -> None:
    background = Image.open(background_path).convert("RGB")
    cutout = Image.open(cutout_path).convert("RGBA")
    logo = Image.open(logo_path).convert("RGBA")
    still = compose_still(
        background, cutout, logo, copy.headline, copy.support, copy.cta, layout, accent
    )
    still.save(still_path)


def build_campaign_receipt(
    project_id: str,
    shots: list[ShotPlan],
    workdir: Path,
    brand: BrandDNA,
    logo_path: str,
    cutout_path: str,
    backgrounds: dict[str, str],
    accent: Color,
    video_path: str | None = None,
    captions_path: str | None = None,
    judge: SemanticJudge | None = None,
    product_sha_expected: str | None = None,
    product_sha_used: str | None = None,
    logo_sha_expected: str | None = None,
    logo_sha_used: str | None = None,
) -> CampaignReceipt:
    product_used = product_sha_used if product_sha_used is not None else _sha256(cutout_path)
    product_expected = product_sha_expected if product_sha_expected is not None else product_used
    logo_used = logo_sha_used if logo_sha_used is not None else _sha256(logo_path)
    logo_expected = logo_sha_expected if logo_sha_expected is not None else logo_used
    palette = [color.hex for color in brand.palette]
    scenes: list[SceneResult] = []
    repairs: list[RepairRecord] = []
    for shot in shots:
        layout: LayoutTemplate = shot.layout_template if is_layout(shot.layout_template) else "center_hero"
        still_path = str(workdir / f"{shot.shot_id}-still.png")
        copy = shot.copy_

        def make_scene(
            active: ShotCopy,
            layout: LayoutTemplate = layout,
            still_path: str = still_path,
            purpose: str = shot.purpose,
            narration: str = shot.narration,
        ) -> SceneAudit:
            return SceneAudit(
                layout=layout, still_path=still_path, cutout_path=cutout_path, logo_path=logo_path,
                headline=active.headline, support=active.support, cta=active.cta,
                palette=palette, required_text=brand.required_text,
                forbidden_claims=brand.forbidden_claims,
                product_sha_expected=product_expected, product_sha_used=product_used,
                logo_sha_expected=logo_expected, logo_sha_used=logo_used,
                purpose=purpose, audience=brand.audience, narration=narration,
            )

        report = audit_scene(make_scene(copy), copy.model_dump(by_alias=True), judge)
        if not report.passed and claims_failed(report.checks) and shot.shot_id in backgrounds:
            fixed = repair_copy(copy, brand.forbidden_claims, brand.required_text)
            _recomposite(backgrounds[shot.shot_id], cutout_path, logo_path, fixed, layout, accent, still_path)
            report = audit_scene(make_scene(fixed), fixed.model_dump(by_alias=True), judge)
            repairs.append(
                RepairRecord(
                    shot_id=shot.shot_id, kind="copy", before_passed=False,
                    after_passed=report.passed,
                    detail="rewrote copy to satisfy claims policy",
                )
            )
            copy = fixed
        scenes.append(
            SceneResult(
                shot_id=shot.shot_id, still_path=still_path, seed=shot.seed,
                checks=report.checks, passed=report.passed,
            )
        )
    receipt = CampaignReceipt(
        project_id=project_id, product_sha256=product_used, logo_sha256=logo_used,
        scenes=scenes, repairs=repairs, video_path=video_path, captions_path=captions_path,
        passed=all(scene.passed for scene in scenes),
    )
    return receipt.finalize()
