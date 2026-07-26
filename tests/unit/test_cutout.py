import numpy as np
from PIL import Image, ImageDraw

from rivet.adapters.cutout import (
    deterministic_alpha,
    existing_alpha,
    flat_background_alpha,
)


def product_on_white() -> Image.Image:
    image = Image.new("RGB", (200, 260), (255, 255, 255))
    ImageDraw.Draw(image).rounded_rectangle([30, 30, 170, 230], radius=24, fill=(36, 36, 40))
    return image


def test_flat_background_is_removed_exactly() -> None:
    alpha = flat_background_alpha(product_on_white())
    assert alpha is not None
    assert alpha[5, 5] == 0
    assert alpha[130, 100] == 255
    coverage = float((alpha > 0).mean())
    assert 0.4 < coverage < 0.7


def test_background_coloured_detail_inside_the_product_stays_opaque() -> None:
    image = product_on_white()
    ImageDraw.Draw(image).ellipse([80, 150, 120, 190], fill=(255, 255, 255))
    alpha = flat_background_alpha(image)
    assert alpha is not None
    assert alpha[170, 100] == 255, "white detail enclosed by the product must not be cut out"


def test_busy_background_is_rejected() -> None:
    noise = np.random.default_rng(7).integers(0, 255, size=(120, 120, 3), dtype=np.uint8)
    assert flat_background_alpha(Image.fromarray(noise, "RGB")) is None


def test_existing_transparency_is_reused() -> None:
    image = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
    ImageDraw.Draw(image).rectangle([20, 20, 80, 80], fill=(200, 60, 20, 255))
    alpha = existing_alpha(image)
    assert alpha is not None
    assert alpha[50, 50] == 255
    assert alpha[5, 5] == 0


def test_opaque_image_has_no_existing_alpha() -> None:
    assert existing_alpha(Image.new("RGB", (40, 40), (10, 10, 10))) is None


def test_deterministic_alpha_prefers_source_transparency() -> None:
    image = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
    ImageDraw.Draw(image).rectangle([10, 10, 40, 40], fill=(9, 9, 9, 255))
    alpha = deterministic_alpha(image)
    assert alpha is not None
    assert alpha[25, 25] == 255


def test_full_bleed_image_is_rejected() -> None:
    assert flat_background_alpha(Image.new("RGB", (80, 80), (12, 200, 90))) is None


def test_cutout_is_reproducible() -> None:
    first = flat_background_alpha(product_on_white())
    second = flat_background_alpha(product_on_white())
    assert first is not None and second is not None
    assert np.array_equal(first, second)
