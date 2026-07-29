from typing import Literal

from rivet.compositor.layouts import LayoutTemplate
from rivet.domain.models import (
    BrandDNA,
    LogoPlacement,
    Motion,
    ProductPlacement,
    ShotCopy,
    ShotPlan,
)
from rivet.pipeline.seeds import derive_seed

BACKGROUND_NEGATIVE = (
    "product, speaker, microphone, headphones, device, gadget, bottle, packaging, "
    # A synthetic human in an advertisement is a likeness problem no brand will
    # accept, and the plain "person, people" pair was not enough to suppress one.
    "person, people, human, man, woman, girl, boy, model, portrait, face, "
    "body, figure, hands, crowd, mannequin, silhouette, "
    "text, letters, words, watermark, logo, signage"
)

_SPECS: tuple[
    tuple[
        Literal["hook", "proof", "cta"],
        LayoutTemplate,
        float,
        Literal["i2v", "controlled"],
        str,
        str,
    ],
    ...,
] = (
    (
        "hook", "center_hero", 4.0, "i2v",
        "Open on the product and grab attention",
        "empty matte studio backdrop with a soft falloff",
    ),
    (
        "proof", "split_proof", 5.0, "controlled",
        "Show the product working and why it matters",
        "bare concrete desk surface with soft directional light",
    ),
    (
        "cta", "cta_lockup", 4.0, "controlled",
        "Close with the call to action",
        "warm minimal gradient backdrop, no objects",
    ),
)


def propose_shots(dna: BrandDNA, campaign_seed: int) -> list[ShotPlan]:
    tone = ", ".join(dna.tone) if dna.tone else "clean, modern"
    cta_text = dna.required_text[0] if dna.required_text else f"Discover {dna.product_name}"
    shots: list[ShotPlan] = []
    for shot_id, layout, duration, motion_mode, purpose, setting in _SPECS:
        shots.append(
            ShotPlan(
                shot_id=shot_id,
                purpose=purpose,
                duration_s=duration,
                background_prompt=f"{setting}, {tone} styling, empty scene, no products, no text",
                negative_prompt=BACKGROUND_NEGATIVE,
                copy=ShotCopy(
                    headline=dna.product_name,
                    support=f"For {dna.audience}" if dna.audience else "",
                    cta=cta_text,
                ),
                product=ProductPlacement(anchor="center", scale=0.5, min_visible_area=0.2),
                logo=LogoPlacement(anchor="top_right", scale=0.12),
                layout_template=layout,
                motion=Motion(mode=motion_mode, camera="pan", intensity=0.3),
                narration=f"{dna.product_name}. {cta_text}." if shot_id == "cta" else dna.product_name,
                seed=derive_seed(campaign_seed, shot_id),
            )
        )
    return shots
