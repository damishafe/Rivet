from rivet.adapters.qwen_planner import safe_background


def test_background_prompt_naming_a_person_is_rejected() -> None:
    assert safe_background("a woman walking through a bright studio", "Kora Arc") == ""
    assert safe_background("a model posing beside a wall", "Kora Arc") == ""


def test_empty_environment_prompt_survives() -> None:
    prompt = "a warm concrete wall with soft window light"
    assert safe_background(prompt, "Kora Arc") == prompt
