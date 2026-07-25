import colorsys
import re
from dataclasses import dataclass, field

import numpy as np
from PIL import Image, ImageDraw

from rivet.audit.semantic import SemanticJudge, check_semantic
from rivet.compositor.compose import contained_box
from rivet.compositor.geometry import GEOMETRY, SAFE_MARGIN, rect_px
from rivet.domain.layouts import LayoutTemplate
from rivet.domain.models import AuditCheck

Color = tuple[int, int, int]


@dataclass
class SceneAudit:
    layout: LayoutTemplate
    still_path: str
    cutout_path: str
    logo_path: str
    headline: str
    support: str
    cta: str
    palette: list[str]
    required_text: list[str]
    forbidden_claims: list[str]
    product_sha_expected: str
    product_sha_used: str
    logo_sha_expected: str
    logo_sha_used: str
    purpose: str = ""
    audience: str = ""
    canvas: tuple[int, int] = (1080, 1920)
    palette_threshold: float = 40.0
    prominence_threshold: float = 0.05
    safe_margin: float = SAFE_MARGIN


def _hex_to_rgb(value: str) -> Color:
    v = value.lstrip("#")
    return (int(v[0:2], 16), int(v[2:4], 16), int(v[4:6], 16))


def _is_neutral(rgb: Color) -> bool:
    high, low = max(rgb), min(rgb)
    saturation = 0.0 if high == 0 else (high - low) / high
    return saturation < 0.30 or high < 45


def _hue(rgb: Color) -> float:
    h, _, _ = colorsys.rgb_to_hsv(rgb[0] / 255, rgb[1] / 255, rgb[2] / 255)
    return h * 360


def _hue_distance(a: float, b: float) -> float:
    diff = abs(a - b) % 360
    return min(diff, 360 - diff)


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


def check_logo_presence(scene: SceneAudit) -> AuditCheck:
    still = np.asarray(Image.open(scene.still_path).convert("RGB"))
    logo = Image.open(scene.logo_path).convert("RGBA")
    box = rect_px(GEOMETRY[scene.layout]["logo"], scene.canvas)
    px, py, placed_w, placed_h = contained_box((logo.width, logo.height), box)
    placed = np.asarray(logo.resize((placed_w, placed_h)))
    region = still[py : py + placed_h, px : px + placed_w]
    opaque = placed[:, :, 3] > 128
    fits = region.shape[0] == placed.shape[0] and region.shape[1] == placed.shape[1]
    if fits and opaque.any():
        diff = np.abs(
            region[opaque].astype(np.float64) - placed[:, :, :3][opaque].astype(np.float64)
        )
        mean_diff = float(diff.mean())
    else:
        mean_diff = 255.0
    ok = mean_diff <= 40.0
    return AuditCheck(
        check_id="A02",
        metric="logo fidelity mean pixel diff",
        threshold="<= 40",
        observed=round(mean_diff, 1),
        passed=ok,
        owner_stage="layout",
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


def check_palette(scene: SceneAudit) -> AuditCheck:
    still = Image.open(scene.still_path).convert("RGB")
    px, py, pw, ph = rect_px(GEOMETRY[scene.layout]["product"], scene.canvas)
    masked = still.copy()
    ImageDraw.Draw(masked).rectangle([px, py, px + pw, py + ph], fill=(0, 0, 0))
    quantized = masked.resize((64, 64)).quantize(6)
    table = quantized.getpalette() or []
    brand_hues = [_hue(_hex_to_rgb(h)) for h in scene.palette if not _is_neutral(_hex_to_rgb(h))]
    indices = np.asarray(quantized).ravel()
    counts = np.bincount(indices, minlength=6)
    worst = 0.0
    for index in counts.argsort()[::-1][:4]:
        base = int(index) * 3
        if counts[index] == 0 or base + 2 >= len(table):
            continue
        rgb = (table[base], table[base + 1], table[base + 2])
        if _is_neutral(rgb) or not brand_hues:
            continue
        nearest = min(_hue_distance(_hue(rgb), hue) for hue in brand_hues)
        worst = max(worst, nearest)
    ok = worst <= scene.palette_threshold
    return AuditCheck(
        check_id="A04",
        metric="saturated colour hue vs palette",
        threshold=f"<= {scene.palette_threshold} degrees",
        observed=round(worst, 1),
        passed=ok,
        owner_stage="background/layout",
    )


def check_safe_area(scene: SceneAudit) -> AuditCheck:
    boxes = GEOMETRY[scene.layout]
    margin = scene.safe_margin
    rects = list(boxes.values())
    inside = all(
        x >= margin and y >= margin and x + w <= 1 - margin and y + h <= 1 - margin
        for x, y, w, h in rects
    )
    overlaps = 0
    keys = list(boxes)
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            ax, ay, aw, ah = boxes[keys[i]]
            bx, by, bw, bh = boxes[keys[j]]
            if ax < bx + bw and bx < ax + aw and ay < by + bh and by < ay + ah:
                overlaps += 1
    ok = inside and overlaps == 0
    return AuditCheck(
        check_id="A05",
        metric="template safe-area (static geometry)",
        threshold="0 violations",
        observed=0 if ok else (overlaps if inside else -1),
        passed=ok,
        owner_stage="layout",
    )


def check_prominence(scene: SceneAudit) -> AuditCheck:
    cutout_image = Image.open(scene.cutout_path).convert("RGBA")
    cutout = np.asarray(cutout_image)
    alpha_fraction = float((cutout[:, :, 3] > 128).mean()) if cutout.size else 0.0
    cw, ch = cutout_image.size
    _, _, box_w, box_h = rect_px(GEOMETRY[scene.layout]["product"], scene.canvas)
    scale = min(box_w / cw, box_h / ch)
    placed_opaque_area = alpha_fraction * cw * ch * scale**2
    canvas_w, canvas_h = scene.canvas
    frame_share = placed_opaque_area / (canvas_w * canvas_h)
    ok = frame_share >= scene.prominence_threshold
    return AuditCheck(
        check_id="A06",
        metric="product share of frame",
        threshold=f">= {scene.prominence_threshold}",
        observed=round(frame_share, 3),
        passed=ok,
        owner_stage="layout/mask",
    )


def check_claims(scene: SceneAudit) -> AuditCheck:
    joined = f"{scene.headline} {scene.support} {scene.cta}".lower()
    forbidden_hits = [
        f
        for f in scene.forbidden_claims
        if re.search(r"\b" + re.escape(f.lower()) + r"\b", joined)
    ]
    missing_required = [r for r in scene.required_text if r.lower() not in joined]
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
    ]
    if judge is not None:
        message = f"{scene.headline} {scene.support} {scene.cta}".strip()
        checks.append(
            check_semantic(scene.still_path, scene.purpose, scene.audience, message, judge)
        )
    return AuditReport(checks=checks)
