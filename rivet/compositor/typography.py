from pathlib import Path

from PIL import ImageDraw, ImageFont

_FONT_PATH = Path(__file__).parent / "fonts" / "Inter.ttf"


def load_font(size: int, weight: int = 400) -> ImageFont.FreeTypeFont:
    font = ImageFont.truetype(str(_FONT_PATH), size)
    font.set_variation_by_axes([14.0, float(weight)])
    return font


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    lines: list[str] = []
    line = ""
    for word in text.split():
        trial = f"{line} {word}".strip()
        if not line or draw.textlength(trial, font=font) <= max_width:
            line = trial
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def fit_lines(
    draw: ImageDraw.ImageDraw,
    text: str,
    max_width: int,
    max_height: int,
    weight: int,
    max_size: int,
    min_size: int = 16,
    line_spacing: float = 1.12,
) -> tuple[ImageFont.FreeTypeFont, list[str], float, bool]:
    for size in range(max_size, min_size - 1, -2):
        font = load_font(size, weight)
        lines = wrap_text(draw, text, font, max_width)
        line_height = size * line_spacing
        fits_height = line_height * len(lines) <= max_height
        fits_width = all(draw.textlength(line, font=font) <= max_width for line in lines)
        if fits_height and fits_width:
            return font, lines, line_height, True
    font = load_font(min_size, weight)
    lines = wrap_text(draw, text, font, max_width)
    line_height = min_size * line_spacing
    fits = line_height * len(lines) <= max_height and all(
        draw.textlength(line, font=font) <= max_width for line in lines
    )
    return font, lines, line_height, fits


def fit_single_line(
    draw: ImageDraw.ImageDraw,
    text: str,
    max_width: int,
    weight: int,
    max_size: int,
    min_size: int = 14,
) -> tuple[ImageFont.FreeTypeFont, bool]:
    for size in range(max_size, min_size - 1, -2):
        font = load_font(size, weight)
        if draw.textlength(text, font=font) <= max_width:
            return font, True
    return load_font(min_size, weight), False
