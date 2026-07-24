from rivet.pipeline.fingerprint import cache_key
from rivet.pipeline.stage import ModelManifest, StageRequest


def make_request(**overrides: object) -> StageRequest:
    base: dict[str, object] = {
        "stage": "background.generate",
        "config": {"width": 768, "height": 1344},
        "seed": 42,
        "input_hashes": ["b" * 64, "a" * 64],
    }
    base.update(overrides)
    return StageRequest.model_validate(base)


MANIFEST = ModelManifest(repo="black-forest-labs/FLUX.1-schnell", revision="abc123", dtype="fp16")


def test_cache_key_is_deterministic() -> None:
    assert cache_key("bg", "1", make_request(), MANIFEST) == cache_key(
        "bg", "1", make_request(), MANIFEST
    )


def test_input_hash_order_does_not_matter() -> None:
    reordered = make_request(input_hashes=["a" * 64, "b" * 64])
    assert cache_key("bg", "1", make_request(), MANIFEST) == cache_key(
        "bg", "1", reordered, MANIFEST
    )


def test_seed_changes_key() -> None:
    assert cache_key("bg", "1", make_request(), MANIFEST) != cache_key(
        "bg", "1", make_request(seed=43), MANIFEST
    )


def test_model_revision_changes_key() -> None:
    other = ModelManifest(repo=MANIFEST.repo, revision="def456", dtype="fp16")
    assert cache_key("bg", "1", make_request(), MANIFEST) != cache_key(
        "bg", "1", make_request(), other
    )


def test_stage_version_changes_key() -> None:
    assert cache_key("bg", "1", make_request(), MANIFEST) != cache_key(
        "bg", "2", make_request(), MANIFEST
    )


def test_missing_manifest_still_produces_key() -> None:
    key = cache_key("transcribe", "1", make_request(), None)
    assert len(key) == 64
