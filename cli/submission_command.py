import re
import subprocess
from pathlib import Path

import typer

REQUIRED_FILES = (
    "README.md",
    "LICENSE",
    "MODEL_LICENSES.md",
    "docs/profile.md",
    "project-profile.pdf",
)

FORBIDDEN_FILES = (
    "CLAUDE.md",
    "PRD-Rivet.md",
    "BrandLock_Director_PRD.md",
    "BrandLock_Director_PRD.docx",
    "j.json",
)

SECRET_PATTERNS = (
    ("GitHub token", re.compile(r"gh[pousr]_[A-Za-z0-9]{16,}")),
    ("GitHub fine-grained token", re.compile(r"github_pat_[A-Za-z0-9_]{20,}")),
    ("Hugging Face token", re.compile(r"\bhf_[A-Za-z0-9]{30,}")),
    ("OpenAI key", re.compile(r"\bsk-[A-Za-z0-9]{32,}")),
    ("AWS access key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("private key block", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
)

MODEL_ID = re.compile(r"resolve_model\(\s*\"([^\"]+)\"")
SHIPPED_DIRS = ("rivet/", "cli/", "services/")
MAX_TRACKED_MB = 50
TEXT_SUFFIXES = {
    ".py", ".md", ".txt", ".toml", ".json", ".yaml", ".yml", ".cfg", ".ini",
    ".ts", ".tsx", ".js", ".jsx", ".css", ".html", ".sh", ".lock",
}


def _tracked_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z"], capture_output=True, text=True, check=True
    )
    return [Path(name) for name in result.stdout.split("\0") if name]


def _report(label: str, ok: bool, detail: str = "") -> bool:
    mark = "  ok" if ok else "FAIL"
    typer.echo(f"  [{mark}] {label}{f' — {detail}' if detail else ''}")
    return ok


def _check_required(tracked: set[str]) -> bool:
    missing = [name for name in REQUIRED_FILES if name not in tracked]
    return _report(
        "required deliverables present",
        not missing,
        "" if not missing else f"missing {missing}",
    )


def _check_forbidden(tracked: set[str]) -> bool:
    leaked = [name for name in FORBIDDEN_FILES if name in tracked]
    return _report(
        "internal planning files excluded",
        not leaked,
        "" if not leaked else f"committed {leaked}",
    )


def _check_secrets(files: list[Path]) -> bool:
    hits: list[str] = []
    for path in files:
        if path.suffix.lower() not in TEXT_SUFFIXES or not path.is_file():
            continue
        try:
            body = path.read_text(errors="ignore")
        except OSError:
            continue
        for label, pattern in SECRET_PATTERNS:
            if pattern.search(body):
                hits.append(f"{path}: {label}")
    return _report("no secrets in tracked files", not hits, "; ".join(hits[:3]))


def _check_model_licenses(files: list[Path]) -> bool:
    licenses = Path("MODEL_LICENSES.md")
    if not licenses.is_file():
        return _report("every model has a license row", False, "MODEL_LICENSES.md missing")
    recorded = licenses.read_text()
    used: set[str] = set()
    for path in files:
        shipped = str(path).startswith(SHIPPED_DIRS)
        if shipped and path.suffix == ".py" and path.is_file():
            used.update(MODEL_ID.findall(path.read_text(errors="ignore")))
    undocumented = sorted(model for model in used if model not in recorded)
    return _report(
        "every model has a license row",
        not undocumented,
        "" if not undocumented else f"undocumented {undocumented}",
    )


def _check_file_sizes(files: list[Path]) -> bool:
    limit = MAX_TRACKED_MB * 1024 * 1024
    heavy = [
        f"{path} ({path.stat().st_size // (1024 * 1024)} MB)"
        for path in files
        if path.is_file() and path.stat().st_size > limit
    ]
    return _report(f"no tracked file over {MAX_TRACKED_MB} MB", not heavy, "; ".join(heavy))


def submission_check() -> None:
    """Verify the repository is ready to submit: deliverables, secrets, licenses, sizes."""
    files = _tracked_files()
    tracked = {str(path) for path in files}
    typer.echo(f"checking {len(files)} tracked files")
    results = [
        _check_required(tracked),
        _check_forbidden(tracked),
        _check_secrets(files),
        _check_model_licenses(files),
        _check_file_sizes(files),
    ]
    if not all(results):
        typer.echo("submission-check: FAIL", err=True)
        raise typer.Exit(code=1)
    typer.echo("submission-check: pass")
