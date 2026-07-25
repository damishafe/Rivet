from PIL import Image, ImageDraw

from rivet.compositor.geometry import GEOMETRY, rect_px
from rivet.compositor.typography import fit_lines, fit_single_line
from rivet.domain.layouts import LayoutTemplate

CANVAS = (1080, 1920)
WHITE = (250, 250, 250)
MUTED = (205, 205, 210)
CTA_FG = (10, 10, 12)

Box = tuple[int, int, int, int]
Color = tuple[int, int, int]


def cover_fit(image: Image.Image, canvas: tuple[int, int]) -> Image.Image:
    canvas_w, canvas_h = canvas
    scale = max(canvas_w / image.width, canvas_h / image.height)
    resized = image.resize((round(image.width * scale), round(image.height * scale)))
    left = (resized.width - canvas_w) // 2
    top = (resized.height - canvas_h) // 2
    return resized.crop((left, top, left + canvas_w, top + canvas_h)).convert("RGB")


def _scrim(base: Image.Image) -> None:
    width, height = base.size
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    start = int(height * 0.55)
    for y in range(start, height):
        alpha = int(150 * (y - start) / (height - start))
        draw.line([(0, y), (width, y)], fill=(5, 5, 8, alpha))
    base.paste(overlay, (0, 0), overlay)


def contained_box(overlay_size: tuple[int, int], box: Box) -> Box:
    overlay_w, overlay_h = overlay_size
    x, y, w, h = box
    scale = min(w / overlay_w, h / overlay_h)
    placed_w = max(1, round(overlay_w * scale))
    placed_h = max(1, round(overlay_h * scale))
    px = x + (w - placed_w) // 2
    py = y + (h - placed_h) // 2
    return (px, py, placed_w, placed_h)


def _place_contained(base: Image.Image, overlay: Image.Image, box: Box) -> None:
    px, py, placed_w, placed_h = contained_box((overlay.width, overlay.height), box)
    resized = overlay.resize((placed_w, placed_h)).convert("RGBA")
    base.paste(resized, (px, py), resized)


def _draw_text(
    draw: ImageDraw.ImageDraw, text: str, box: Box, weight: int, color: Color, centered: bool
) -> None:
    if not text:
        return
    x, y, w, h = box
    font, lines, line_height, _ = fit_lines(draw, text, w, h, weight, max_size=min(h, 150))
    ty = float(y)
    for line in lines:
        line_width = draw.textlength(line, font=font)
        tx = x + (w - line_width) / 2 if centered else x
        draw.text((tx, ty), line, font=font, fill=color)
        ty += line_height


def _draw_cta(draw: ImageDraw.ImageDraw, text: str, box: Box, accent: Color) -> None:
    if not text:
        return
    x, y, w, h = box
    draw.rounded_rectangle([x, y, x + w, y + h], radius=h // 2, fill=accent)
    font, _ = fit_single_line(draw, text, int(w * 0.82), weight=700, max_size=int(h * 0.5))
    ascent, descent = font.getmetrics()
    tx = x + (w - draw.textlength(text, font=font)) / 2
    ty = y + (h - (ascent + descent)) / 2
    draw.text((tx, ty), text, font=font, fill=CTA_FG)


def compose_still(
    background: Image.Image,
    cutout: Image.Image,
    logo: Image.Image,
    headline: str,
    support: str,
    cta: str,
    layout: LayoutTemplate,
    accent: Color,
    canvas: tuple[int, int] = CANVAS,
) -> Image.Image:
    base = cover_fit(background, canvas)
    _scrim(base)
    draw = ImageDraw.Draw(base, "RGBA")
    geo = GEOMETRY[layout]
    _place_contained(base, cutout, rect_px(geo["product"], canvas))
    _place_contained(base, logo, rect_px(geo["logo"], canvas))
    centered = layout != "split_proof"
    _draw_text(draw, headline, rect_px(geo["headline"], canvas), 800, WHITE, centered)
    _draw_text(draw, support, rect_px(geo["support"], canvas), 400, MUTED, centered)
    _draw_cta(draw, cta, rect_px(geo["cta"], canvas), accent)
    return base
