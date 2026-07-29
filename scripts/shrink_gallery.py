"""Shrink the gallery to web-sized images that a repository should carry.

The showcase writes full-resolution stills and the assembled videos, which is right
for inspection and wrong for git: a 1080x1920 PNG per scene plus two MP4s is several
megabytes, and some networks refuse a push that large. Full resolution stills and the
video ship inside the export pack, which is where they belong.
"""

import sys
from pathlib import Path

from PIL import Image

GALLERY = Path("docs/gallery")
WIDTH = 540
QUALITY = 82


def main() -> int:
    if not GALLERY.is_dir():
        print(f"no {GALLERY}; run scripts/showcase.py first", file=sys.stderr)
        return 1

    saved = 0
    for png in sorted(GALLERY.glob("*.png")):
        with Image.open(png) as image:
            scale = WIDTH / image.width
            small = image.convert("RGB").resize(
                (WIDTH, round(image.height * scale)), Image.LANCZOS
            )
        jpg = png.with_suffix(".jpg")
        small.save(jpg, "JPEG", quality=QUALITY, optimize=True)
        saved += png.stat().st_size - jpg.stat().st_size
        png.unlink()
        print(f"  {png.name} -> {jpg.name} ({jpg.stat().st_size // 1024} KB)")

    for mp4 in sorted(GALLERY.glob("*.mp4")):
        print(f"  dropped {mp4.name} ({mp4.stat().st_size // 1024} KB) — ships in the pack")
        saved += mp4.stat().st_size
        mp4.unlink()

    readme = GALLERY / "README.md"
    if readme.is_file():
        body = readme.read_text().replace(".png", ".jpg")
        kept = [
            line
            for line in body.splitlines()
            if not (line.startswith("[") and ".mp4)" in line)
        ]
        kept.append("")
        kept.append(
            "Full-resolution stills, the assembled video, the receipt and a manifest "
            "hashing every member ship inside each campaign's export pack."
        )
        readme.write_text("\n".join(kept))

    total = sum(f.stat().st_size for f in GALLERY.iterdir() if f.is_file())
    print(f"gallery is now {total // 1024} KB (saved {saved // 1024} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
