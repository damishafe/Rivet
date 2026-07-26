import re
from collections.abc import Callable

from rivet.adapters.model_cache import resolve_model
from rivet.domain.models import AuditCheck
from rivet.pipeline.device import resolve_device

SemanticJudge = Callable[[str, str], tuple[int, str]]
SEMANTIC_THRESHOLD = 80


def qwen_judge(image_path: str, question: str) -> tuple[int, str]:
    import torch
    from PIL import Image
    from transformers import AutoProcessor, Qwen3VLForConditionalGeneration

    name = resolve_model("Qwen/Qwen3-VL-4B-Instruct")
    device = resolve_device()
    proc = AutoProcessor.from_pretrained(name)
    model = Qwen3VLForConditionalGeneration.from_pretrained(name, dtype=torch.float16).to(device)
    image = Image.open(image_path).convert("RGB")
    messages = [
        {
            "role": "user",
            "content": [{"type": "image", "image": image}, {"type": "text", "text": question}],
        }
    ]
    inputs = proc.apply_chat_template(
        messages, tokenize=True, add_generation_prompt=True, return_dict=True, return_tensors="pt"
    ).to(device)
    out = model.generate(**inputs, max_new_tokens=80, do_sample=False)
    text = proc.batch_decode(
        out[:, inputs["input_ids"].shape[1] :], skip_special_tokens=True
    )[0].strip()
    match = re.search(r"\b(\d{1,3})\b", text)
    score = min(int(match.group(1)), 100) if match else 0
    return score, text


def check_semantic(
    still_path: str,
    purpose: str,
    audience: str,
    message: str,
    judge: SemanticJudge,
    threshold: int = SEMANTIC_THRESHOLD,
) -> AuditCheck:
    question = (
        f"Rate from 0 to 100 how well this vertical ad image fits audience '{audience}', "
        f"scene purpose '{purpose}', and message '{message}'. Begin your reply with the number."
    )
    try:
        score, rationale = judge(still_path, question)
    except Exception as error:
        return AuditCheck(
            check_id="A08",
            metric="semantic alignment score",
            threshold=f">= {threshold}",
            observed=f"judge unavailable: {error}"[:96],
            passed=False,
            owner_stage="plan/background",
            advisory=True,
        )
    return AuditCheck(
        check_id="A08",
        metric="semantic alignment score",
        threshold=f">= {threshold}",
        observed=f"{score} — {rationale[:80]}",
        passed=score >= threshold,
        owner_stage="plan/background",
        advisory=True,
    )
