"""Draw the demo brands.

Three products in different categories, shapes and palettes, so a reviewer can see
the pipeline is not tuned to one silhouette. Everything here is deterministic
drawing: no model runs, and the assets are original rather than licensed imagery.
"""

import sys
from pathlib import Path

from PIL import Image, ImageDraw

from rivet.compositor.typography import load_font

FIXTURES = Path("fixtures")


def _logo(name: str, accent: tuple[int, int, int], out: Path) -> None:
    image = Image.new("RGBA", (560, 150), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.ellipse([12, 45, 72, 105], fill=accent)
    draw.ellipse([30, 63, 54, 87], fill=(10, 10, 12, 255))
    font = load_font(58, 600)
    draw.text((92, 44), name, font=font, fill=(250, 250, 250, 255))
    image.save(out)


def kora_arc(out: Path) -> None:
    image = Image.new("RGBA", (520, 640), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle([60, 40, 460, 600], radius=96, fill=(34, 34, 38, 255))
    draw.rounded_rectangle([60, 40, 460, 600], radius=96, outline=(64, 64, 70, 255), width=3)
    for row in range(9):
        for col in range(9):
            x = 150 + col * 25
            y = 150 + row * 25
            draw.ellipse([x, y, x + 11, y + 11], fill=(22, 22, 26, 255))
    draw.ellipse([215, 470, 305, 560], outline=(255, 59, 0, 255), width=7)
    draw.line([260, 492, 260, 538], fill=(255, 59, 0, 255), width=7)
    image.save(out)


def lumen_flask(out: Path) -> None:
    image = Image.new("RGBA", (520, 640), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle([170, 30, 350, 96], radius=26, fill=(206, 212, 218, 255))
    draw.rounded_rectangle([150, 90, 370, 610], radius=72, fill=(232, 236, 240, 255))
    draw.rounded_rectangle([150, 90, 370, 610], radius=72, outline=(178, 186, 194, 255), width=3)
    draw.rounded_rectangle([186, 150, 232, 560], radius=22, fill=(255, 255, 255, 90))
    draw.rounded_rectangle([150, 300, 370, 392], radius=10, fill=(23, 132, 176, 255))
    font = load_font(34, 600)
    draw.text((196, 328), "LUMEN", font=font, fill=(255, 255, 255, 255))
    image.save(out)


def terra_press(out: Path) -> None:
    image = Image.new("RGBA", (520, 640), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.polygon([(120, 250), (400, 250), (368, 596), (152, 596)], fill=(84, 58, 42, 255))
    draw.polygon([(120, 250), (400, 250), (392, 288), (128, 288)], fill=(104, 74, 54, 255))
    draw.rounded_rectangle([196, 96, 324, 262], radius=18, fill=(58, 40, 30, 255))
    draw.rounded_rectangle([222, 60, 298, 112], radius=14, fill=(140, 104, 72, 255))
    draw.ellipse([214, 380, 306, 472], fill=(212, 168, 116, 255))
    image.save(out)


BRANDS = (
    ("kora-arc", "Kora Arc", kora_arc, (255, 59, 0)),
    ("lumen-flask", "Lumen", lumen_flask, (23, 132, 176)),
    ("terra-press", "Terra", terra_press, (196, 132, 74)),
)


def _crop_to_content(path: Path) -> None:
    """A real cutout is tight to the product; padding would understate its frame share."""
    image = Image.open(path)
    box = image.getbbox()
    if box:
        image.crop(box).save(path)


def main() -> int:
    for slug, wordmark, draw_product, accent in BRANDS:
        folder = FIXTURES / slug
        folder.mkdir(parents=True, exist_ok=True)
        draw_product(folder / "product.png")
        _crop_to_content(folder / "product.png")
        _logo(wordmark, accent, folder / "logo.png")
        print(f"  {slug}: product.png logo.png")
    print(f"wrote {len(BRANDS)} brand fixtures")
    return 0


if __name__ == "__main__":
    sys.exit(main())
