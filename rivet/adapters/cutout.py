import numpy as np
from PIL import Image, ImageDraw, ImageFilter

SENTINELS = ((255, 0, 255), (0, 255, 1), (255, 1, 0), (1, 1, 254))
BORDER_TOLERANCE = 18
MIN_COVERAGE = 0.02
MAX_COVERAGE = 0.95


def existing_alpha(image: Image.Image) -> np.ndarray | None:
    if image.mode not in ("RGBA", "LA", "PA"):
        return None
    alpha = np.asarray(image.convert("RGBA"))[:, :, 3]
    if alpha.min() > 250:
        return None
    return np.asarray(alpha, dtype=np.uint8)


def _border_is_uniform(pixels: np.ndarray, tolerance: int) -> bool:
    edges = np.concatenate(
        [pixels[0], pixels[-1], pixels[:, 0], pixels[:, -1]]
    ).astype(np.int16)
    spread = edges.max(axis=0) - edges.min(axis=0)
    return bool(spread.max() <= tolerance)


def _unused_sentinel(pixels: np.ndarray) -> tuple[int, int, int] | None:
    for candidate in SENTINELS:
        if not bool(np.all(pixels == np.array(candidate), axis=-1).any()):
            return candidate
    return None


def flat_background_alpha(
    image: Image.Image, tolerance: int = BORDER_TOLERANCE
) -> np.ndarray | None:
    rgb = image.convert("RGB")
    pixels = np.asarray(rgb)
    if not _border_is_uniform(pixels, tolerance):
        return None
    sentinel = _unused_sentinel(pixels)
    if sentinel is None:
        return None
    work = rgb.copy()
    width, height = work.size
    for corner in ((0, 0), (width - 1, 0), (0, height - 1), (width - 1, height - 1)):
        ImageDraw.floodfill(work, corner, sentinel, thresh=tolerance)
    background = np.all(np.asarray(work) == np.array(sentinel), axis=-1)
    alpha = np.where(background, 0, 255).astype(np.uint8)
    coverage = float((alpha > 0).mean())
    if not MIN_COVERAGE <= coverage <= MAX_COVERAGE:
        return None
    return alpha


def deterministic_alpha(image: Image.Image) -> np.ndarray | None:
    found = existing_alpha(image)
    if found is not None:
        return found
    return flat_background_alpha(image)


def write_cutout(image: Image.Image, alpha: np.ndarray, out_path: str) -> None:
    smoothed = Image.fromarray(alpha).filter(ImageFilter.GaussianBlur(0.6))
    rgba = np.dstack([np.asarray(image.convert("RGB")), np.asarray(smoothed)])
    Image.fromarray(rgba, "RGBA").save(out_path)
