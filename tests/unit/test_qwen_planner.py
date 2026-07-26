import json

import pytest

from rivet.adapters.qwen_planner import (
    LIMITS,
    SPOKEN_CHARS_PER_SECOND,
    build_prompt,
    parse_scenes,
    propose_shots_vlm,
)
from rivet.domain.models import BrandDNA, PaletteColor

SCENES = {
    "scenes": [
        {
            "shot_id": "hook",
            "headline": "Sound that fills the room",
            "support": "Built for small studios and dorm desks",
            "cta": "Hear it now",
            "narration": "Kora Arc turns any corner into a studio.",
            "background_prompt": "warm empty desk at golden hour, no text",
        },
        {
            "shot_id": "proof",
            "headline": "Twelve hours per charge",
            "support": "One cable, no adapters, no fuss",
            "cta": "See the specs",
            "narration": "Twelve hours of playback on a single charge.",
            "background_prompt": "clean concrete studio wall, soft light",
        },
        {
            "shot_id": "cta",
            "headline": "Make it yours",
            "support": "Free returns within thirty days",
            "cta": "Shop Kora Arc",
            "narration": "Shop Kora Arc today.",
            "background_prompt": "minimal warm gradient backdrop",
        },
    ]
}


def brand() -> BrandDNA:
    return BrandDNA(
        product_name="Kora Arc",
        palette=[PaletteColor(hex="#FF3B00", role="primary")],
        tone=["bold"],
        audience="campus creators",
        required_text=[],
        forbidden_claims=["waterproof"],
        logo_asset_id="a" * 32,
        product_asset_id="b" * 32,
    )


def writer_of(payload: str):  # type: ignore[no-untyped-def]
    def _writer(image_path: str, prompt: str) -> str:
        return payload

    return _writer


def test_vlm_copy_is_distinct_per_scene() -> None:
    shots = propose_shots_vlm(brand(), 7, "p.png", "", writer_of(json.dumps(SCENES)))
    assert [s.shot_id for s in shots] == ["hook", "proof", "cta"]
    headlines = [s.copy_.headline for s in shots]
    assert len(set(headlines)) == 3
    assert all(s.copy_.support for s in shots)
    assert len({s.narration for s in shots}) == 3
    assert shots[0].copy_.headline == "Sound that fills the room"


def test_prose_wrapped_json_still_parses() -> None:
    noisy = f"Sure! Here is the JSON:\n```json\n{json.dumps(SCENES)}\n```\nHope that helps."
    shots = propose_shots_vlm(brand(), 7, "p.png", "", writer_of(noisy))
    assert shots[1].copy_.headline == "Twelve hours per charge"


def test_overlong_copy_is_clipped_to_limits() -> None:
    payload = {
        "scenes": [
            {
                "shot_id": "hook",
                "headline": "An extraordinarily long headline that would overflow its box",
                "support": "s",
                "cta": "c",
            }
        ]
    }
    shots = propose_shots_vlm(brand(), 7, "p.png", "", writer_of(json.dumps(payload)))
    assert len(shots[0].copy_.headline) <= LIMITS["headline"]


@pytest.mark.parametrize("payload", ["not json at all", "{}", '{"scenes": []}', ""])
def test_unusable_output_falls_back_to_heuristic(payload: str) -> None:
    shots = propose_shots_vlm(brand(), 7, "p.png", "", writer_of(payload))
    assert [s.shot_id for s in shots] == ["hook", "proof", "cta"]
    assert all(s.copy_.headline == "Kora Arc" for s in shots)


def test_writer_failure_falls_back_to_heuristic() -> None:
    def broken(image_path: str, prompt: str) -> str:
        raise RuntimeError("model unavailable")

    shots = propose_shots_vlm(brand(), 7, "p.png", "", broken)
    assert len(shots) == 3
    assert shots[0].copy_.headline == "Kora Arc"


def test_missing_scene_keeps_heuristic_baseline_for_that_shot() -> None:
    partial = {"scenes": [SCENES["scenes"][0]]}
    shots = propose_shots_vlm(brand(), 7, "p.png", "", writer_of(json.dumps(partial)))
    assert shots[0].copy_.headline == "Sound that fills the room"
    assert shots[1].copy_.headline == "Kora Arc"


def test_plan_shape_matches_heuristic_contract() -> None:
    vlm = propose_shots_vlm(brand(), 7, "p.png", "", writer_of(json.dumps(SCENES)))
    fallback = propose_shots_vlm(brand(), 7, "p.png", "", writer_of("garbage"))
    for produced, expected in zip(vlm, fallback, strict=True):
        assert produced.layout_template == expected.layout_template
        assert produced.duration_s == expected.duration_s
        assert produced.seed == expected.seed
        assert produced.motion == expected.motion


def test_narration_is_clipped_to_scene_duration() -> None:
    long_line = "This narration is far too long to be spoken aloud within a short scene."
    payload = {"scenes": [{"shot_id": s, "narration": long_line} for s in ("hook", "proof", "cta")]}
    shots = propose_shots_vlm(brand(), 7, "p.png", "", writer_of(json.dumps(payload)))
    for shot in shots:
        spoken_seconds = len(shot.narration) / SPOKEN_CHARS_PER_SECOND
        assert spoken_seconds <= shot.duration_s, f"{shot.shot_id} narration overruns its scene"


def test_background_naming_the_product_is_rejected() -> None:
    payload = {
        "scenes": [
            {
                "shot_id": "hook",
                "background_prompt": "studio centered on a matte black speaker with orange button",
            },
            {"shot_id": "proof", "background_prompt": "neutral wall behind the Kora Arc"},
            {"shot_id": "cta", "background_prompt": "warm empty gradient wall, soft light"},
        ]
    }
    shots = propose_shots_vlm(brand(), 7, "p.png", "", writer_of(json.dumps(payload)))
    assert "speaker" not in shots[0].background_prompt.lower()
    assert "kora arc" not in shots[1].background_prompt.lower()
    assert shots[2].background_prompt == "warm empty gradient wall, soft light"


def test_every_shot_carries_a_background_negative_prompt() -> None:
    for shots in (
        propose_shots_vlm(brand(), 7, "p.png", "", writer_of(json.dumps(SCENES))),
        propose_shots_vlm(brand(), 7, "p.png", "", writer_of("garbage")),
    ):
        for shot in shots:
            assert "product" in shot.negative_prompt
            assert "text" in shot.negative_prompt


def test_prompt_carries_brand_constraints() -> None:
    prompt = build_prompt(brand(), "launch for campus creators")
    assert "waterproof" in prompt
    assert "campus creators" in prompt
    assert "#FF3B00" in prompt


def test_parse_scenes_ignores_unknown_shot_ids() -> None:
    payload = json.dumps({"scenes": [{"shot_id": "outro", "headline": "x"}]})
    assert parse_scenes(payload) == {}
