from collections import Counter
from io import BytesIO
from typing import cast

import numpy as np
from PIL import Image

from rivet.domain.models import BrandDNA, PaletteColor

ROLES = ("primary", "secondary", "accent", "background")


def propose_palette(data: bytes, count: int = 4) -> list[PaletteColor]:
    with Image.open(BytesIO(data)) as source:
        image = source.convert("RGB").resize((64, 64), Image.Resampling.NEAREST)
    quantized = image.quantize(count)
    palette_data: list[int] = quantized.getpalette() or []
    frequencies: Counter[int] = Counter(cast(list[int], quantized.get_flattened_data()))
    colors: list[PaletteColor] = []
    for rank, (index, _count) in enumerate(frequencies.most_common(count)):
        r, g, b = palette_data[index * 3 : index * 3 + 3]
        colors.append(
            PaletteColor(hex=f"#{r:02X}{g:02X}{b:02X}", role=ROLES[rank % len(ROLES)])
        )
    return colors


def brand_mark_color(data: bytes) -> PaletteColor | None:
    with Image.open(BytesIO(data)) as source:
        image = source.convert("RGBA").resize((64, 64), Image.Resampling.NEAREST)
    pixels = np.asarray(image).reshape(-1, 4).astype(np.int16)
    rgb, alpha = pixels[:, :3], pixels[:, 3]
    high, low = rgb.max(axis=1), rgb.min(axis=1)
    saturation = (high - low) / np.maximum(high, 1)
    opaque_chromatic = (alpha > 200) & (saturation >= 0.35) & (high >= 60)
    if not opaque_chromatic.any():
        return None
    colors, counts = np.unique(rgb[opaque_chromatic], axis=0, return_counts=True)
    r, g, b = (int(value) for value in colors[counts.argmax()])
    return PaletteColor(hex=f"#{r:02X}{g:02X}{b:02X}", role="primary")


def propose_palette_with_logo(product_image: bytes, logo_image: bytes | None) -> list[PaletteColor]:
    mark = brand_mark_color(logo_image) if logo_image is not None else None
    if mark is None:
        return propose_palette(product_image)
    supporting = propose_palette(product_image, count=3)
    roles = ("secondary", "accent", "background")
    return [mark] + [
        PaletteColor(hex=color.hex, role=roles[index % len(roles)])
        for index, color in enumerate(supporting)
    ]


def propose_brand_dna(
    project_name: str,
    product_asset_id: str,
    logo_asset_id: str,
    product_image: bytes,
    logo_image: bytes | None = None,
) -> BrandDNA:
    return BrandDNA(
        product_name=project_name,
        palette=propose_palette_with_logo(product_image, logo_image),
        tone=[],
        audience="",
        required_text=[],
        forbidden_claims=[],
        logo_asset_id=logo_asset_id,
        product_asset_id=product_asset_id,
        confirmed_at=None,
    )
