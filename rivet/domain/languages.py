"""The languages a campaign can be produced in.

An advertisement is checked in the language it ships in. Narrating in Portuguese while
auditing an English claim list would verify nothing, so the language chosen here drives
the voice, the typography and the claims the audit reads.

Each entry names the Kokoro language code and voice, and the font that can actually draw
the script — Inter covers Latin and nothing else, so a language whose font is missing is
rejected at validation rather than rendered as empty boxes.
"""

from typing import Literal

from pydantic import BaseModel

LanguageCode = Literal["en", "es", "fr", "it", "pt", "zh"]


class Language(BaseModel):
    code: LanguageCode
    name: str
    kokoro_code: str
    voice: str
    font: str
    prompt_name: str


LANGUAGES: dict[LanguageCode, Language] = {
    "en": Language(
        code="en", name="English", kokoro_code="a", voice="af_heart",
        font="Inter.ttf", prompt_name="English",
    ),
    "es": Language(
        code="es", name="Español", kokoro_code="e", voice="ef_dora",
        font="Inter.ttf", prompt_name="Spanish",
    ),
    "fr": Language(
        code="fr", name="Français", kokoro_code="f", voice="ff_siwis",
        font="Inter.ttf", prompt_name="French",
    ),
    "it": Language(
        code="it", name="Italiano", kokoro_code="i", voice="if_sara",
        font="Inter.ttf", prompt_name="Italian",
    ),
    "pt": Language(
        code="pt", name="Português", kokoro_code="p", voice="pf_dora",
        font="Inter.ttf", prompt_name="Brazilian Portuguese",
    ),
    "zh": Language(
        code="zh", name="中文", kokoro_code="z", voice="zf_xiaobei",
        font="NotoSansSC.ttf", prompt_name="Simplified Chinese",
    ),
}

DEFAULT_LANGUAGE: LanguageCode = "en"


def language(code: LanguageCode | str | None) -> Language:
    if code is None:
        return LANGUAGES[DEFAULT_LANGUAGE]
    for candidate in LANGUAGES.values():
        if candidate.code == code:
            return candidate
    raise ValueError(f"unsupported language: {code}")
