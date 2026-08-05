"""Re-compose a finished campaign into the other delivery formats.

A brand needs the same campaign as a story, a square feed post and a wide banner.
Each one is composited from the same protected assets and audited on its own terms,
because a layout that is legible when it is tall is not automatically legible when
it is wide.
"""

from pathlib import Path

from PIL import Image

from rivet.audit.checks import audit_scene
from rivet.audit.scene import SceneAudit
from rivet.compositor.compose import compose_still
from rivet.compositor.geometry import CANVASES, Format
from rivet.domain.languages import language
from rivet.domain.models import BrandDNA, ShotPlan
from rivet.domain.receipt import SceneResult

Color = tuple[int, int, int]
EXTRA_FORMATS: tuple[Format, ...] = ("feed", "banner")


def render_formats(
    shots: list[ShotPlan],
    workdir: Path,
    brand: BrandDNA,
    logo_path: str,
    cutout_path: str,
    backgrounds: dict[str, str],
    accent: Color,
    product_sha: tuple[str, str],
    logo_sha: tuple[str, str],
    formats: tuple[Format, ...] = EXTRA_FORMATS,
) -> list[SceneResult]:
    palette = [color.hex for color in brand.palette]
    cutout = Image.open(cutout_path).convert("RGBA")
    logo = Image.open(logo_path).convert("RGBA")
    results: list[SceneResult] = []

    for shot in shots:
        source = backgrounds.get(shot.shot_id)
        if source is None or not Path(source).is_file():
            continue
        background = Image.open(source).convert("RGB")
        for fmt in formats:
            still_path = workdir / f"{shot.shot_id}-{fmt}.png"
            compose_still(
                background,
                cutout,
                logo,
                shot.copy_.headline,
                shot.copy_.support,
                shot.copy_.cta,
                shot.layout_template,
                accent,
                fmt=fmt,
                font_name=language(brand.language).font,
            ).save(still_path)

            scene = SceneAudit(
                layout=shot.layout_template,
                still_path=str(still_path),
                cutout_path=cutout_path,
                logo_path=logo_path,
                headline=shot.copy_.headline,
                support=shot.copy_.support,
                cta=shot.copy_.cta,
                palette=palette,
                required_text=brand.required_text,
                forbidden_claims=brand.forbidden_claims,
                product_sha_expected=product_sha[0],
                product_sha_used=product_sha[1],
                logo_sha_expected=logo_sha[0],
                logo_sha_used=logo_sha[1],
                purpose=shot.purpose,
                audience=brand.audience,
                narration=shot.narration,
                format=fmt,
                canvas=CANVASES[fmt],
            )
            report = audit_scene(scene, shot.copy_.model_dump(by_alias=True))
            results.append(
                SceneResult(
                    shot_id=shot.shot_id,
                    still_path=str(still_path),
                    seed=shot.seed,
                    checks=report.checks,
                    passed=report.passed,
                    format=fmt,
                )
            )
    return results
