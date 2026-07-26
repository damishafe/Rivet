import numpy as np
from PIL import Image, ImageDraw

from rivet.audit.scene import SceneAudit, hex_to_rgb, hue, hue_distance, is_neutral
from rivet.compositor.compose import MUTED, WHITE, contained_box
from rivet.compositor.contrast import LEGIBILITY_FLOOR, contrast_ratio
from rivet.compositor.geometry import GEOMETRY, rect_px
from rivet.compositor.typography import fit_lines, fit_single_line
from rivet.domain.models import AuditCheck

TEXT_INK_DISTANCE = 90


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


def check_product_fidelity(scene: SceneAudit) -> AuditCheck:
    still = np.asarray(Image.open(scene.still_path).convert("RGB"))
    product = Image.open(scene.cutout_path).convert("RGBA")
    box = rect_px(GEOMETRY[scene.layout]["product"], scene.canvas)
    px, py, placed_w, placed_h = contained_box((product.width, product.height), box)
    placed = np.asarray(product.resize((placed_w, placed_h)))
    region = still[py : py + placed_h, px : px + placed_w]
    opaque = placed[:, :, 3] > 250
    fits = region.shape[0] == placed.shape[0] and region.shape[1] == placed.shape[1]
    if fits and opaque.any():
        diff = np.abs(
            region[opaque].astype(np.float64) - placed[:, :, :3][opaque].astype(np.float64)
        )
        mean_diff = float(diff.mean())
    else:
        mean_diff = 255.0
    ok = mean_diff <= 10.0
    return AuditCheck(
        check_id="A09",
        metric="product fidelity mean pixel diff",
        threshold="<= 10",
        observed=round(mean_diff, 1),
        passed=ok,
        owner_stage="compose",
    )


def _background_under_text(patch: np.ndarray, color: tuple[int, int, int]) -> tuple[int, int, int]:
    ink = np.abs(patch.astype(np.int16) - np.array(color, dtype=np.int16)).sum(axis=1)
    background = patch[ink > TEXT_INK_DISTANCE]
    sample = background if background.size else patch
    return (
        round(float(sample[:, 0].mean())),
        round(float(sample[:, 1].mean())),
        round(float(sample[:, 2].mean())),
    )


def check_legibility(scene: SceneAudit) -> AuditCheck:
    still = Image.open(scene.still_path).convert("RGB")
    boxes = GEOMETRY[scene.layout]
    worst = 21.0
    for key, color, text in (
        ("headline", WHITE, scene.headline),
        ("support", MUTED, scene.support),
    ):
        if not text:
            continue
        x, y, w, h = rect_px(boxes[key], scene.canvas)
        patch = np.asarray(still.crop((x, y, x + w, y + h))).reshape(-1, 3)
        worst = min(worst, contrast_ratio(_background_under_text(patch, color), color))
    ok = worst >= LEGIBILITY_FLOOR
    return AuditCheck(
        check_id="A10",
        metric="text contrast ratio",
        threshold=f">= {LEGIBILITY_FLOOR}:1",
        observed=round(worst, 2),
        passed=ok,
        owner_stage="layout",
    )


def check_palette(scene: SceneAudit) -> AuditCheck:
    still = Image.open(scene.still_path).convert("RGB")
    px, py, pw, ph = rect_px(GEOMETRY[scene.layout]["product"], scene.canvas)
    masked = still.copy()
    ImageDraw.Draw(masked).rectangle([px, py, px + pw, py + ph], fill=(0, 0, 0))
    quantized = masked.resize((64, 64)).quantize(6)
    table = quantized.getpalette() or []
    brand_hues = [hue(hex_to_rgb(h)) for h in scene.palette if not is_neutral(hex_to_rgb(h))]
    indices = np.asarray(quantized).ravel()
    counts = np.bincount(indices, minlength=6)
    floor = max(1, int(counts.sum()) // 20)
    worst = 0.0
    for index in counts.argsort()[::-1]:
        base = int(index) * 3
        if counts[index] < floor or base + 2 >= len(table):
            continue
        rgb = (table[base], table[base + 1], table[base + 2])
        if is_neutral(rgb):
            continue
        if not brand_hues:
            worst = max(worst, scene.palette_threshold + 1.0)
            continue
        nearest = min(hue_distance(hue(rgb), brand) for brand in brand_hues)
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


def _text_overflow(scene: SceneAudit, boxes: dict[str, tuple[float, float, float, float]]) -> int:
    scratch = ImageDraw.Draw(Image.new("RGB", scene.canvas))
    count = 0
    for key, weight, text in (("headline", 800, scene.headline), ("support", 400, scene.support)):
        if not text:
            continue
        _, _, bw, bh = rect_px(boxes[key], scene.canvas)
        _, _, _, fits = fit_lines(scratch, text, bw, bh, weight, max_size=min(bh, 150))
        if not fits:
            count += 1
    if scene.cta:
        _, _, cw, ch = rect_px(boxes["cta"], scene.canvas)
        _, fits = fit_single_line(scratch, scene.cta, int(cw * 0.82), 700, int(ch * 0.5))
        if not fits:
            count += 1
    return count


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
    overflow = _text_overflow(scene, boxes)
    ok = inside and overlaps == 0 and overflow == 0
    return AuditCheck(
        check_id="A05",
        metric="safe-area geometry and rendered text overflow",
        threshold="0 violations",
        observed=0 if ok else (overlaps + overflow if inside else -1),
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
        metric="planned product share of frame",
        threshold=f">= {scene.prominence_threshold}",
        observed=round(frame_share, 3),
        passed=ok,
        owner_stage="layout/mask",
    )
