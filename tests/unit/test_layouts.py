from rivet.compositor.layouts import LAYOUTS, is_layout


def test_three_templates_in_order() -> None:
    assert LAYOUTS == ("center_hero", "split_proof", "cta_lockup")


def test_is_layout_accepts_known() -> None:
    assert is_layout("center_hero") is True


def test_is_layout_rejects_unknown() -> None:
    assert is_layout("fancy_grid") is False
