import hashlib


def derive_seed(campaign_seed: int, label: str) -> int:
    digest = hashlib.sha256(f"{campaign_seed}:{label}".encode()).hexdigest()
    return int(digest[:8], 16)
