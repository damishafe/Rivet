from collections import Counter
from io import BytesIO
from typing import cast

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


def propose_brand_dna(
    project_name: str, product_asset_id: str, logo_asset_id: str, product_image: bytes
) -> BrandDNA:
    return BrandDNA(
        product_name=project_name,
        palette=propose_palette(product_image),
        tone=[],
        audience="",
        required_text=[],
        forbidden_claims=[],
        logo_asset_id=logo_asset_id,
        product_asset_id=product_asset_id,
        confirmed_at=None,
    )
