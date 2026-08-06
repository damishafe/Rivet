import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FONT_DIR = Path(__file__).parent / "fonts"
DEFAULT_FONT = "Inter.ttf"

CJK = re.compile(r"[　-ヿ㐀-䶿一-鿿豈-﫿＀-￯]")
NOTDEF_PROBE = chr(0xE0FF)


class MissingFont(RuntimeError):
    pass


def font_path(name: str = DEFAULT_FONT) -> Path:
    """The bundled font for a script.

    A missing font is an error, not a fallback: PIL will happily draw every glyph as an
    empty box, which passes rendering and fails a reader.
    """
    path = FONT_DIR / name
    if not path.is_file():
        raise MissingFont(f"{name} is not bundled in {FONT_DIR}")
    return path


def load_font(size: int, weight: int = 400, name: str = DEFAULT_FONT) -> ImageFont.FreeTypeFont:
    font = ImageFont.truetype(str(font_path(name)), size)
    try:
        font.set_variation_by_axes([14.0, float(weight)])
    except OSError:
        pass
    return font


def _glyph_bytes(char: str, font: ImageFont.FreeTypeFont) -> bytes:
    box = int(font.size) * 3
    canvas = Image.new("L", (box, box), 0)
    ImageDraw.Draw(canvas).text((box / 3, box / 3), char, font=font, fill=255)
    return canvas.tobytes()


def missing_glyphs(text: str, font: ImageFont.FreeTypeFont) -> list[str]:
    """Characters this font cannot draw.

    A font without the script still renders: every absent codepoint becomes the same
    .notdef box. Comparing each glyph against the box a private-use codepoint produces
    tells a real character apart from a placeholder one.
    """
    probe = _glyph_bytes(NOTDEF_PROBE, font)
    return [
        char
        for char in dict.fromkeys(text)
        if not char.isspace() and _glyph_bytes(char, font) == probe
    ]


def _tokenize(text: str) -> list[str]:
    """Split into the smallest pieces a line may break at.

    Chinese is written without spaces, so whitespace tokens leave a headline as one
    unbreakable word that can only be met by shrinking it to nothing.
    """
    tokens: list[str] = []
    for word in text.split():
        if CJK.search(word):
            tokens.extend(word)
        else:
            tokens.append(word)
    return tokens


def _extend(line: str, token: str) -> str:
    if not line:
        return token
    if CJK.search(token) or CJK.search(line[-1]):
        return f"{line}{token}"
    return f"{line} {token}"


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    lines: list[str] = []
    line = ""
    for token in _tokenize(text):
        trial = _extend(line, token)
        if not line or draw.textlength(trial, font=font) <= max_width:
            line = trial
        else:
            lines.append(line)
            line = token
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
    font_name: str = DEFAULT_FONT,
) -> tuple[ImageFont.FreeTypeFont, list[str], float, bool]:
    for size in range(max_size, min_size - 1, -2):
        font = load_font(size, weight, font_name)
        lines = wrap_text(draw, text, font, max_width)
        line_height = size * line_spacing
        fits_height = line_height * len(lines) <= max_height
        fits_width = all(draw.textlength(line, font=font) <= max_width for line in lines)
        if fits_height and fits_width:
            return font, lines, line_height, True
    font = load_font(min_size, weight, font_name)
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
    font_name: str = DEFAULT_FONT,
) -> tuple[ImageFont.FreeTypeFont, bool]:
    for size in range(max_size, min_size - 1, -2):
        font = load_font(size, weight, font_name)
        if draw.textlength(text, font=font) <= max_width:
            return font, True
    return load_font(min_size, weight, font_name), False
