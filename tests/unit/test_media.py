from io import BytesIO

import pytest
from PIL import Image

from rivet.domain.media import (
    InvalidMedia,
    MediaTooLarge,
    UnsupportedMediaType,
    validate_upload,
)


def png_bytes(mode: str = "RGB", size: tuple[int, int] = (8, 6)) -> bytes:
    buffer = BytesIO()
    color: tuple[int, ...] = (255, 0, 0) if mode == "RGB" else (255, 0, 0, 128)
    Image.new(mode, size, color).save(buffer, format="PNG")
    return buffer.getvalue()


def test_product_png_sniffed_with_dimensions() -> None:
    media = validate_upload("product", png_bytes(), "application/octet-stream")
    assert (media.mime, media.suffix, media.width, media.height) == ("image/png", ".png", 8, 6)


def test_product_rejects_non_image_bytes() -> None:
    with pytest.raises(InvalidMedia):
        validate_upload("product", b"definitely not an image", "image/png")


def test_product_rejects_oversized(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("rivet.domain.media.MAX_IMAGE_BYTES", 10)
    with pytest.raises(MediaTooLarge):
        validate_upload("product", png_bytes(), None)


def test_logo_requires_alpha_png() -> None:
    with pytest.raises(InvalidMedia):
        validate_upload("logo", png_bytes("RGB"), "image/png")
    media = validate_upload("logo", png_bytes("RGBA"), "image/png")
    assert media.mime == "image/png"


def test_logo_accepts_svg() -> None:
    media = validate_upload("logo", b'<svg xmlns="http://www.w3.org/2000/svg"></svg>', None)
    assert (media.mime, media.suffix) == ("image/svg+xml", ".svg")


def test_brief_audio_by_declared_mime() -> None:
    media = validate_upload("brief_audio", b"RIFFxxxxWAVE", "audio/wav")
    assert (media.mime, media.suffix) == ("audio/wav", ".wav")
    with pytest.raises(UnsupportedMediaType):
        validate_upload("brief_audio", b"data", "video/mp4")


def test_derived_role_never_accepted() -> None:
    with pytest.raises(UnsupportedMediaType):
        validate_upload("derived", png_bytes(), "image/png")


def test_product_rejects_truncated_png() -> None:
    truncated = png_bytes()[:40]
    with pytest.raises(InvalidMedia):
        validate_upload("product", truncated, "image/png")
