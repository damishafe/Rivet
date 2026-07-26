import json
import os
import re
from collections.abc import Callable
from typing import Any

from rivet.adapters.heuristic_planner import propose_shots
from rivet.domain.models import BrandDNA, ShotCopy, ShotPlan
from rivet.pipeline.device import resolve_device

SceneWriter = Callable[[str, str], str]

LIMITS = {"headline": 28, "support": 48, "cta": 22, "background_prompt": 220}
SHOT_IDS = ("hook", "proof", "cta")
BANNED_BACKGROUND_WORDS = (
    "speaker", "microphone", "headphone", "earbud", "device", "gadget", "product",
    "bottle", "phone", "laptop", "camera", "watermark", "logo",
)
SPOKEN_CHARS_PER_SECOND = 15
SPOKEN_OVERSHOOT = 1.2


def narration_limit(duration_s: float) -> int:
    return max(40, int(duration_s * SPOKEN_CHARS_PER_SECOND))


def qwen_writer(image_path: str, prompt: str) -> str:
    import torch
    from PIL import Image
    from transformers import AutoProcessor, Qwen3VLForConditionalGeneration

    name = "Qwen/Qwen3-VL-4B-Instruct"
    device = resolve_device()
    proc = AutoProcessor.from_pretrained(name)
    model = Qwen3VLForConditionalGeneration.from_pretrained(name, dtype=torch.float16).to(device)
    image = Image.open(image_path).convert("RGB")
    messages = [
        {
            "role": "user",
            "content": [{"type": "image", "image": image}, {"type": "text", "text": prompt}],
        }
    ]
    inputs = proc.apply_chat_template(
        messages, tokenize=True, add_generation_prompt=True, return_dict=True, return_tensors="pt"
    ).to(device)
    out = model.generate(**inputs, max_new_tokens=512, do_sample=False)
    decoded = proc.batch_decode(
        out[:, inputs["input_ids"].shape[1] :], skip_special_tokens=True
    )[0]
    return str(decoded).strip()


def build_prompt(dna: BrandDNA, brief: str) -> str:
    palette = ", ".join(color.hex for color in dna.palette[:3])
    tone = ", ".join(dna.tone) if dna.tone else "clean, modern"
    audience = dna.audience or "general consumers"
    required = ", ".join(dna.required_text) or "none"
    forbidden = ", ".join(dna.forbidden_claims) or "none"
    return (
        f"You are an advertising copywriter. Study the product image.\n"
        f"Product: {dna.product_name}\nAudience: {audience}\nTone: {tone}\n"
        f"Brief: {brief or 'introduce the product honestly'}\n"
        f"Brand colours: {palette}\n"
        f"Required phrases (use verbatim in at least one scene): {required}\n"
        f"Forbidden claims (never use): {forbidden}\n\n"
        "Write a three-scene vertical video advert. Reply with JSON only:\n"
        '{"scenes":[{"shot_id":"hook","headline":"","support":"","cta":"",'
        '"narration":"","background_prompt":""}]}\n\n'
        "Rules:\n"
        f"- headline at most {LIMITS['headline']} characters\n"
        f"- support at most {LIMITS['support']} characters\n"
        f"- cta at most {LIMITS['cta']} characters\n"
        "- narration is one short complete sentence spoken aloud over the scene and must fit "
        f"its length: at most {narration_limit(4.0)} characters for hook and cta, "
        f"{narration_limit(5.0)} for proof\n"
        "- background_prompt describes ONLY the empty environment behind the product: "
        "surfaces, materials, light and colour. The product is added afterwards, so never "
        "mention the product, a speaker, a microphone, a device or any object that could be "
        "mistaken for it, and never mention people, text or logos. Keep colours neutral or "
        "close to the brand colours\n"
        "- give all three shot_ids: hook, proof, cta\n"
        "- each scene must say something different: hook grabs attention, proof gives a "
        "concrete reason to believe, cta closes with the action\n"
        "- never invent specifications, certifications, awards or superlatives"
    )


def _clean(value: Any, limit: int) -> str:
    if not isinstance(value, str):
        return ""
    text = re.sub(r"\s+", " ", value).strip().strip('"').strip()
    if len(text) <= limit:
        return text
    clipped = text[:limit].rsplit(" ", 1)[0]
    return (clipped or text[:limit]).rstrip(",;:-")


def parse_scenes(raw: str) -> dict[str, dict[str, Any]]:
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if match is None:
        return {}
    payload = json.loads(match.group(0))
    entries = payload.get("scenes") if isinstance(payload, dict) else payload
    if not isinstance(entries, list):
        return {}
    scenes: dict[str, dict[str, Any]] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        shot_id = str(entry.get("shot_id", "")).strip().lower()
        if shot_id in SHOT_IDS:
            scenes[shot_id] = entry
    return scenes


def clip_narration(text: str, limit: int) -> str:
    spoken = re.sub(r"\s+", " ", text).strip().strip('"').strip()
    if len(spoken) <= limit:
        return spoken
    kept = ""
    for sentence in re.findall(r"[^.!?]+[.!?]?", spoken):
        candidate = f"{kept}{sentence}".strip()
        if len(candidate) > limit:
            break
        kept = f"{candidate} "
    complete = kept.strip()
    if complete:
        return complete
    first = re.split(r"(?<=[.!?])\s+", spoken)[0].strip()
    if first and len(first) <= limit * SPOKEN_OVERSHOOT:
        return first
    clipped = spoken[:limit].rsplit(" ", 1)[0].rstrip(",;:- ")
    return f"{clipped}." if clipped else spoken[:limit]


def safe_background(prompt: str, product_name: str) -> str:
    lowered = prompt.lower()
    banned = [word for word in BANNED_BACKGROUND_WORDS if word in lowered]
    if banned or (product_name and product_name.lower() in lowered):
        return ""
    return prompt


def _merge(shot: ShotPlan, fields: dict[str, Any], product_name: str) -> ShotPlan:
    copy_ = ShotCopy(
        headline=_clean(fields.get("headline"), LIMITS["headline"]) or shot.copy_.headline,
        support=_clean(fields.get("support"), LIMITS["support"]) or shot.copy_.support,
        cta=_clean(fields.get("cta"), LIMITS["cta"]) or shot.copy_.cta,
    )
    spoken = fields.get("narration")
    narration = (
        clip_narration(spoken, narration_limit(shot.duration_s))
        if isinstance(spoken, str)
        else ""
    ) or shot.narration
    background = (
        safe_background(
            _clean(fields.get("background_prompt"), LIMITS["background_prompt"]), product_name
        )
        or shot.background_prompt
    )
    return shot.model_copy(
        update={"copy_": copy_, "narration": narration, "background_prompt": background}
    )


def resolve_writer(writer: SceneWriter | None) -> SceneWriter | None:
    if writer is not None:
        return writer
    return None if os.environ.get("RIVET_NO_VLM") else qwen_writer


def propose_shots_vlm(
    dna: BrandDNA,
    campaign_seed: int,
    product_image_path: str,
    brief: str = "",
    writer: SceneWriter | None = None,
) -> list[ShotPlan]:
    baseline = propose_shots(dna, campaign_seed)
    active = resolve_writer(writer)
    if active is None:
        return baseline
    try:
        scenes = parse_scenes(active(product_image_path, build_prompt(dna, brief)))
    except Exception:
        return baseline
    if not scenes:
        return baseline
    return [
        _merge(shot, scenes.get(shot.shot_id, {}), dna.product_name) for shot in baseline
    ]
