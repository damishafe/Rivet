import shutil
import sys

import typer

from rivet import __version__


def check(label: str, ok: bool, detail: str) -> bool:
    mark = "ok" if ok else "MISSING"
    typer.echo(f"  [{mark:>7}] {label}: {detail}")
    return ok


def _torch_detail() -> str | None:
    try:
        import torch
    except ImportError:
        return None
    device = "cuda/rocm" if torch.cuda.is_available() else "cpu"
    return f"{torch.__version__} ({device})"


def doctor() -> None:
    """Verify python, ffmpeg and the torch device are usable."""
    typer.echo(f"rivet {__version__} doctor")
    ffmpeg = shutil.which("ffmpeg")
    torch_detail = _torch_detail()
    required = [
        check("python", sys.version_info >= (3, 11), sys.version.split()[0]),
        check("ffmpeg", ffmpeg is not None, ffmpeg or "not found"),
    ]
    check(
        "torch",
        torch_detail is not None,
        torch_detail or "not installed (expected on dev machines; required on the W7900 box)",
    )
    if not all(required):
        raise typer.Exit(code=1)
