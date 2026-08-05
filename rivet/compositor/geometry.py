from typing import Literal

from rivet.domain.layouts import LayoutTemplate

Rect = tuple[float, float, float, float]
Format = Literal["story", "feed", "banner"]

SAFE_MARGIN = 0.04

CANVASES: dict[Format, tuple[int, int]] = {
    "story": (1080, 1920),
    "feed": (1080, 1080),
    "banner": (1920, 1080),
}

GEOMETRY: dict[LayoutTemplate, dict[str, Rect]] = {
    "center_hero": {
        "logo": (0.40, 0.06, 0.20, 0.05),
        "product": (0.19, 0.30, 0.62, 0.40),
        "headline": (0.08, 0.73, 0.84, 0.10),
        "support": (0.12, 0.835, 0.76, 0.05),
        "cta": (0.28, 0.89, 0.44, 0.055),
    },
    "split_proof": {
        "logo": (0.08, 0.07, 0.20, 0.045),
        "product": (0.50, 0.28, 0.46, 0.44),
        "headline": (0.08, 0.30, 0.40, 0.18),
        "support": (0.08, 0.50, 0.40, 0.14),
        "cta": (0.08, 0.88, 0.42, 0.055),
    },
    "cta_lockup": {
        "logo": (0.40, 0.09, 0.20, 0.05),
        "product": (0.26, 0.16, 0.48, 0.33),
        "headline": (0.08, 0.50, 0.84, 0.14),
        "support": (0.14, 0.65, 0.72, 0.06),
        "cta": (0.20, 0.75, 0.60, 0.08),
    },
}

FEED_GEOMETRY: dict[str, Rect] = {
    "logo": (0.40, 0.06, 0.20, 0.07),
    "product": (0.26, 0.17, 0.48, 0.42),
    "headline": (0.07, 0.635, 0.86, 0.115),
    "support": (0.12, 0.765, 0.76, 0.055),
    "cta": (0.30, 0.85, 0.40, 0.08),
}

BANNER_GEOMETRY: dict[str, Rect] = {
    "logo": (0.06, 0.08, 0.14, 0.075),
    "product": (0.56, 0.13, 0.36, 0.74),
    "headline": (0.06, 0.30, 0.44, 0.20),
    "support": (0.06, 0.545, 0.42, 0.085),
    "cta": (0.06, 0.70, 0.26, 0.11),
}

_BY_FORMAT: dict[Format, dict[str, Rect] | None] = {
    "story": None,
    "feed": FEED_GEOMETRY,
    "banner": BANNER_GEOMETRY,
}


def geometry_for(layout: LayoutTemplate, fmt: Format = "story") -> dict[str, Rect]:
    """Regions for a layout in a given aspect.

    A vertical layout does not survive being squashed into a banner: the boxes keep
    their proportions and collide. Feed and banner carry their own composition, and
    only the vertical story format varies by layout.
    """
    override = _BY_FORMAT[fmt]
    return GEOMETRY[layout] if override is None else override


def rect_px(rect: Rect, canvas: tuple[int, int]) -> tuple[int, int, int, int]:
    width, height = canvas
    x, y, w, h = rect
    return (round(x * width), round(y * height), round(w * width), round(h * height))
