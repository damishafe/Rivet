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


def test_chinese_lines_do_not_open_with_punctuation_or_strand_a_character() -> None:
    """CJK breaks anywhere, so width-only wrapping strands commas and single ideographs."""
    from PIL import Image, ImageDraw

    from rivet.compositor.typography import load_font, wrap_text

    draw = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    font = load_font(72, 800, "NotoSansSC.ttf")
    for width in (420, 520, 640):
        lines = wrap_text(draw, "清晰音质，自然呈现", font, width)
        assert all(not line.startswith("，") for line in lines), lines
        assert all(len(line) > 1 for line in lines), lines


def test_latin_wrapping_still_breaks_on_words() -> None:
    from PIL import Image, ImageDraw

    from rivet.compositor.typography import load_font, wrap_text

    draw = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    lines = wrap_text(draw, "Make every space your studio", load_font(60, 400), 520)
    assert all(" " in line or line.count(" ") == 0 for line in lines)
    assert "".join(lines).replace(" ", "") == "Makeeveryspaceyourstudio"
