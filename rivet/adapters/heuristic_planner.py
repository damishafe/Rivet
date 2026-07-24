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

_SPECS: tuple[
    tuple[
        Literal["hook", "proof", "cta"],
        LayoutTemplate,
        float,
        Literal["i2v", "controlled"],
        str,
    ],
    ...,
] = (
    ("hook", "center_hero", 4.0, "i2v", "Open on the product and grab attention"),
    ("proof", "split_proof", 5.0, "controlled", "Show the product working and why it matters"),
    ("cta", "cta_lockup", 4.0, "controlled", "Close with the call to action"),
)


def propose_shots(dna: BrandDNA, campaign_seed: int) -> list[ShotPlan]:
    tone = ", ".join(dna.tone) if dna.tone else "clean, modern"
    cta_text = dna.required_text[0] if dna.required_text else f"Discover {dna.product_name}"
    shots: list[ShotPlan] = []
    for shot_id, layout, duration, motion_mode, purpose in _SPECS:
        shots.append(
            ShotPlan(
                shot_id=shot_id,
                purpose=purpose,
                duration_s=duration,
                background_prompt=f"{tone} scene for {dna.product_name}, {shot_id}",
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
