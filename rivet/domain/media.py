from io import BytesIO

from PIL import Image, UnidentifiedImageError
from pydantic import BaseModel

from rivet.domain.models import AssetRole

MAX_IMAGE_BYTES = 20 * 1024 * 1024
MAX_AUDIO_BYTES = 25 * 1024 * 1024

IMAGE_SUFFIXES = {"PNG": ".png", "JPEG": ".jpg", "WEBP": ".webp"}
IMAGE_MIMES = {"PNG": "image/png", "JPEG": "image/jpeg", "WEBP": "image/webp"}
AUDIO_MIMES = {
    "audio/wav": ".wav",
    "audio/x-wav": ".wav",
    "audio/mpeg": ".mp3",
    "audio/mp4": ".m4a",
    "audio/x-m4a": ".m4a",
}


class UnsupportedMediaType(ValueError):
    pass


class MediaTooLarge(ValueError):
    pass


class InvalidMedia(ValueError):
    pass


class ValidatedMedia(BaseModel):
    mime: str
    suffix: str
    width: int | None = None
    height: int | None = None


def _probe_image(data: bytes) -> tuple[str, int, int, bool]:
    try:
        with Image.open(BytesIO(data)) as image:
            image_format = image.format or ""
            width, height = image.size
            has_alpha = image.mode in ("RGBA", "LA", "PA") or "transparency" in image.info
    except UnidentifiedImageError as error:
        raise InvalidMedia("unrecognized image content") from error
    if image_format not in IMAGE_SUFFIXES:
        raise UnsupportedMediaType(f"unsupported image format {image_format}")
    return image_format, width, height, has_alpha


def _is_svg(data: bytes) -> bool:
    head = data[:512].lstrip().lower()
    return head.startswith(b"<svg") or (head.startswith(b"<?xml") and b"<svg" in head)


def _validate_image(data: bytes) -> ValidatedMedia:
    if len(data) > MAX_IMAGE_BYTES:
        raise MediaTooLarge("image exceeds 20MB")
    image_format, width, height, _ = _probe_image(data)
    return ValidatedMedia(
        mime=IMAGE_MIMES[image_format],
        suffix=IMAGE_SUFFIXES[image_format],
        width=width,
        height=height,
    )


def _validate_logo(data: bytes) -> ValidatedMedia:
    if len(data) > MAX_IMAGE_BYTES:
        raise MediaTooLarge("logo exceeds 20MB")
    if _is_svg(data):
        return ValidatedMedia(mime="image/svg+xml", suffix=".svg")
    image_format, width, height, has_alpha = _probe_image(data)
    if image_format != "PNG" or not has_alpha:
        raise InvalidMedia("logo must be a transparent png or svg")
    return ValidatedMedia(mime="image/png", suffix=".png", width=width, height=height)


def _validate_audio(data: bytes, declared_mime: str | None) -> ValidatedMedia:
    if len(data) > MAX_AUDIO_BYTES:
        raise MediaTooLarge("audio exceeds 25MB")
    if declared_mime not in AUDIO_MIMES:
        raise UnsupportedMediaType(f"unsupported audio type {declared_mime}")
    return ValidatedMedia(mime=declared_mime, suffix=AUDIO_MIMES[declared_mime])


def validate_upload(role: AssetRole, data: bytes, declared_mime: str | None) -> ValidatedMedia:
    if role in ("product", "style_ref"):
        return _validate_image(data)
    if role == "logo":
        return _validate_logo(data)
    if role == "brief_audio":
        return _validate_audio(data, declared_mime)
    raise UnsupportedMediaType(f"role {role} cannot be uploaded")
