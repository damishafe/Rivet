from PIL import Image

from rivet.compositor.compose import compose_still
from rivet.compositor.geometry import GEOMETRY
from rivet.domain.layouts import LAYOUTS


def synthetic() -> tuple[Image.Image, Image.Image, Image.Image]:
    background = Image.new("RGB", (832, 1216), (60, 60, 66))
    cutout = Image.new("RGBA", (200, 200), (255, 90, 0, 255))
    logo = Image.new("RGBA", (120, 40), (250, 250, 250, 255))
    return background, cutout, logo


def test_every_layout_renders_full_canvas() -> None:
    background, cutout, logo = synthetic()
    for layout in LAYOUTS:
        still = compose_still(
            background, cutout, logo, "Kora Arc", "Make every space your studio", "Shop now",
            layout, (255, 59, 0),
        )
        assert still.size == (1080, 1920)
        assert still.mode == "RGB"


def test_geometry_covers_all_templates() -> None:
    assert set(GEOMETRY) == set(LAYOUTS)
    for boxes in GEOMETRY.values():
        assert set(boxes) == {"logo", "product", "headline", "support", "cta"}


def test_empty_copy_still_renders() -> None:
    background, cutout, logo = synthetic()
    still = compose_still(background, cutout, logo, "", "", "", "center_hero", (255, 59, 0))
    assert still.size == (1080, 1920)
