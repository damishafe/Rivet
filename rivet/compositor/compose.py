import numpy as np
from PIL import Image, ImageDraw

from rivet.compositor.contrast import SCRIM_RGB, needed_darkening
from rivet.compositor.geometry import CANVASES, Format, geometry_for, rect_px
from rivet.compositor.typography import DEFAULT_FONT, fit_lines, fit_single_line
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


def _mean_color(base: Image.Image, box: Box) -> Color:
    x, y, w, h = box
    patch = np.asarray(base.crop((x, y, x + w, y + h)).convert("RGB")).reshape(-1, 3)
    return (
        round(float(patch[:, 0].mean())),
        round(float(patch[:, 1].mean())),
        round(float(patch[:, 2].mean())),
    )


def _legibility_scrim(
    base: Image.Image,
    layout: LayoutTemplate,
    headline: str,
    support: str,
    canvas: tuple[int, int],
    fmt: Format,
) -> None:
    geo = geometry_for(layout, fmt)
    strongest = 0.0
    for key, color, text in (("headline", WHITE, headline), ("support", MUTED, support)):
        if not text:
            continue
        measured = _mean_color(base, rect_px(geo[key], canvas))
        strongest = max(strongest, needed_darkening(measured, color))
    if strongest <= 0:
        return
    veil = Image.new("RGBA", base.size, (*SCRIM_RGB, round(strongest * 255)))
    base.paste(veil, (0, 0), veil)


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
    draw: ImageDraw.ImageDraw,
    text: str,
    box: Box,
    weight: int,
    color: Color,
    centered: bool,
    font_name: str = DEFAULT_FONT,
) -> None:
    if not text:
        return
    x, y, w, h = box
    font, lines, line_height, _ = fit_lines(
        draw, text, w, h, weight, max_size=min(h, 150), font_name=font_name
    )
    ty = float(y)
    for line in lines:
        line_width = draw.textlength(line, font=font)
        tx = x + (w - line_width) / 2 if centered else x
        draw.text((tx, ty), line, font=font, fill=color)
        ty += line_height


def _draw_cta(
    draw: ImageDraw.ImageDraw, text: str, box: Box, accent: Color, font_name: str = DEFAULT_FONT
) -> None:
    if not text:
        return
    x, y, w, h = box
    draw.rounded_rectangle([x, y, x + w, y + h], radius=h // 2, fill=accent)
    font, _ = fit_single_line(
        draw, text, int(w * 0.82), weight=700, max_size=int(h * 0.5), font_name=font_name
    )
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
    canvas: tuple[int, int] | None = None,
    fmt: Format = "story",
    font_name: str = DEFAULT_FONT,
) -> Image.Image:
    canvas = canvas or CANVASES[fmt]
    base = cover_fit(background, canvas)
    _legibility_scrim(base, layout, headline, support, canvas, fmt)
    _scrim(base)
    draw = ImageDraw.Draw(base, "RGBA")
    geo = geometry_for(layout, fmt)
    _place_contained(base, cutout, rect_px(geo["product"], canvas))
    _place_contained(base, logo, rect_px(geo["logo"], canvas))
    centered = fmt == "feed" or (fmt == "story" and layout != "split_proof")
    _draw_text(draw, headline, rect_px(geo["headline"], canvas), 800, WHITE, centered, font_name)
    _draw_text(draw, support, rect_px(geo["support"], canvas), 400, MUTED, centered, font_name)
    _draw_cta(draw, cta, rect_px(geo["cta"], canvas), accent, font_name)
    return base
