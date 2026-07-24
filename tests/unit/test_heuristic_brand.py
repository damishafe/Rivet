from io import BytesIO

from PIL import Image

from rivet.adapters.heuristic_brand import propose_brand_dna, propose_palette


def two_tone_png() -> bytes:
    image = Image.new("RGB", (10, 10), (255, 59, 0))
    for x in range(5):
        for y in range(10):
            image.putpixel((x, y), (5, 5, 5))
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def test_palette_extracts_dominant_colors_with_roles() -> None:
    palette = propose_palette(two_tone_png(), count=2)
    assert len(palette) == 2
    assert [color.role for color in palette] == ["primary", "secondary"]
    hexes = {color.hex.lower() for color in palette}
    assert any(h in hexes for h in ("#ff3b00", "#050505"))


def test_palette_is_deterministic() -> None:
    assert propose_palette(two_tone_png()) == propose_palette(two_tone_png())


def test_propose_brand_dna_is_unconfirmed_proposal() -> None:
    dna = propose_brand_dna("Kora Arc Launch", "a" * 32, "b" * 32, two_tone_png())
    assert dna.product_name == "Kora Arc Launch"
    assert dna.confirmed_at is None
    assert dna.product_asset_id == "a" * 32
    assert dna.logo_asset_id == "b" * 32
    assert len(dna.palette) >= 1
