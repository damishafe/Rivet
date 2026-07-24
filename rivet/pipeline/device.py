import importlib.util
from typing import Literal

Device = Literal["cuda", "mps", "cpu"]


def resolve_device() -> Device:
    if importlib.util.find_spec("torch") is None:
        return "cpu"
    import torch

    if torch.cuda.is_available():
        return "cuda"
    if torch.backends.mps.is_available():
        return "mps"
    return "cpu"
