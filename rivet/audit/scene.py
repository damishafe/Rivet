import colorsys
import re
from dataclasses import dataclass

from rivet.compositor.geometry import SAFE_MARGIN, Format
from rivet.compositor.typography import DEFAULT_FONT
from rivet.domain.layouts import LayoutTemplate

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
    narration: str = ""
    font: str = DEFAULT_FONT
    format: Format = "story"
    canvas: tuple[int, int] = (1080, 1920)
    palette_threshold: float = 40.0
    prominence_threshold: float = 0.05
    safe_margin: float = SAFE_MARGIN


def hex_to_rgb(value: str) -> Color:
    v = value.lstrip("#")
    return (int(v[0:2], 16), int(v[2:4], 16), int(v[4:6], 16))


def is_neutral(rgb: Color) -> bool:
    high, low = max(rgb), min(rgb)
    saturation = 0.0 if high == 0 else (high - low) / high
    return saturation < 0.30 or high < 45


def hue(rgb: Color) -> float:
    h, _, _ = colorsys.rgb_to_hsv(rgb[0] / 255, rgb[1] / 255, rgb[2] / 255)
    return h * 360


def hue_distance(a: float, b: float) -> float:
    diff = abs(a - b) % 360
    return min(diff, 360 - diff)


def mentions(phrase: str, text: str) -> bool:
    return re.search(r"(?<!\w)" + re.escape(phrase.lower()) + r"(?!\w)", text) is not None
