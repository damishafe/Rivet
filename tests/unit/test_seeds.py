from rivet.pipeline.seeds import derive_seed


def test_deterministic_for_same_inputs() -> None:
    assert derive_seed(42, "hook") == derive_seed(42, "hook")


def test_label_changes_seed() -> None:
    assert derive_seed(42, "hook") != derive_seed(42, "proof")


def test_campaign_seed_changes_seed() -> None:
    assert derive_seed(42, "hook") != derive_seed(43, "hook")


def test_within_uint32_range() -> None:
    seed = derive_seed(999999, "background")
    assert 0 <= seed < 2**32
