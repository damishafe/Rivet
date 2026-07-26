import importlib.util

from rivet.pipeline.device import resolve_device

MB = 1024 * 1024


def _torch_available() -> bool:
    return importlib.util.find_spec("torch") is not None


def reset_peak() -> None:
    if not _torch_available():
        return
    import torch

    device = resolve_device()
    if device == "cuda":
        torch.cuda.reset_peak_memory_stats()


def peak_mb() -> int | None:
    if not _torch_available():
        return None
    import torch

    device = resolve_device()
    if device == "cuda":
        return int(torch.cuda.max_memory_allocated() // MB)
    if device == "mps":
        return int(torch.mps.driver_allocated_memory() // MB)
    return None


def accelerator_report() -> dict[str, str]:
    report: dict[str, str] = {"device": resolve_device()}
    if not _torch_available():
        report["torch"] = "not installed"
        return report
    import torch

    report["torch"] = str(torch.__version__)
    if report["device"] == "cuda":
        report["accelerator"] = torch.cuda.get_device_name(0)
        report["hip"] = str(getattr(torch.version, "hip", "") or "n/a")
        report["cuda"] = str(getattr(torch.version, "cuda", "") or "n/a")
        total = torch.cuda.get_device_properties(0).total_memory
        report["total_vram_mb"] = str(total // MB)
    return report
