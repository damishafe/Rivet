Color = tuple[int, int, int]

SCRIM_RGB: Color = (5, 5, 8)
CONTRAST_TARGET = 4.5
LEGIBILITY_FLOOR = 4.0
MAX_DARKENING = 0.82


def _channel(value: int) -> float:
    v = value / 255
    return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4


def relative_luminance(rgb: Color) -> float:
    r, g, b = (_channel(value) for value in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(first: Color, second: Color) -> float:
    high, low = sorted((relative_luminance(first), relative_luminance(second)), reverse=True)
    return (high + 0.05) / (low + 0.05)


def _blend(background: Color, alpha: float) -> Color:
    return (
        round(background[0] * (1 - alpha) + SCRIM_RGB[0] * alpha),
        round(background[1] * (1 - alpha) + SCRIM_RGB[1] * alpha),
        round(background[2] * (1 - alpha) + SCRIM_RGB[2] * alpha),
    )


def needed_darkening(
    background: Color, foreground: Color, target: float = CONTRAST_TARGET
) -> float:
    if contrast_ratio(background, foreground) >= target:
        return 0.0
    low, high = 0.0, MAX_DARKENING
    for _ in range(12):
        middle = (low + high) / 2
        if contrast_ratio(_blend(background, middle), foreground) >= target:
            high = middle
        else:
            low = middle
    return high
