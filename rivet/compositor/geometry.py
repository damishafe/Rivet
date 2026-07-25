from rivet.domain.layouts import LayoutTemplate

Rect = tuple[float, float, float, float]

SAFE_MARGIN = 0.06

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
        "logo": (0.40, 0.10, 0.20, 0.05),
        "product": (0.30, 0.20, 0.40, 0.26),
        "headline": (0.08, 0.50, 0.84, 0.14),
        "support": (0.14, 0.65, 0.72, 0.06),
        "cta": (0.20, 0.75, 0.60, 0.08),
    },
}


def rect_px(rect: Rect, canvas: tuple[int, int]) -> tuple[int, int, int, int]:
    width, height = canvas
    x, y, w, h = rect
    return (round(x * width), round(y * height), round(w * width), round(h * height))
