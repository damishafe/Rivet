#!/usr/bin/env bash
# One command to make Rivet runnable on a Radeon box.
#
# Everything here was learned the hard way on the contest hardware: the ROCm torch
# belongs to an interpreter that is often not first on PATH, Kokoro pip-installs a
# spaCy model mid-generation unless it is already present, and the model cache must
# live on persistent storage or every session pays the download again.
set -euo pipefail

cd "$(dirname "$0")"

say() { printf '\n\033[1m==> %s\033[0m\n' "$1"; }
warn() { printf '    \033[33m%s\033[0m\n' "$1"; }

# ---------------------------------------------------------------- interpreter
find_python() {
  for candidate in "${RIVET_PYTHON:-}" /opt/venv/bin/python python3 python; do
    [ -n "$candidate" ] || continue
    resolved="$(command -v "$candidate" 2>/dev/null)" || continue
    if "$resolved" -c "import torch" >/dev/null 2>&1; then
      printf '%s' "$resolved"
      return 0
    fi
  done
  command -v python3 || printf 'python3'
}

PYTHON="$(find_python)"
say "python"
echo "    $PYTHON"
"$PYTHON" - <<'PY' || true
import torch
name = torch.cuda.get_device_name(0) if torch.cuda.is_available() else "no GPU"
hip = getattr(torch.version, "hip", None) or "n/a"
print(f"    torch {torch.__version__} | {name} | ROCm {hip}")
PY

BEFORE="$("$PYTHON" -c 'import torch;print(torch.__version__)' 2>/dev/null || echo none)"

# ---------------------------------------------------------------- model cache
say "model cache"
if [ -z "${MODEL_DIR:-}" ]; then
  for candidate in /persistent /workspace "$HOME"; do
    if [ -d "$candidate" ] && [ -w "$candidate" ]; then
      MODEL_DIR="$candidate/rivet-models"
      break
    fi
  done
  MODEL_DIR="${MODEL_DIR:-$HOME/rivet-models}"
fi
mkdir -p "$MODEL_DIR/hub"
export HF_HOME="$MODEL_DIR" HF_HUB_CACHE="$MODEL_DIR/hub"
echo "    $HF_HUB_CACHE"
case "$MODEL_DIR" in
  /persistent/*) ;;
  *) warn "not on a persistent volume — a new instance will download again" ;;
esac

# ---------------------------------------------------------------- ffmpeg
say "ffmpeg"
if command -v ffmpeg >/dev/null; then
  echo "    $(ffmpeg -version | head -1 | cut -c1-60)"
else
  if command -v apt-get >/dev/null; then
    APT="apt-get"
    [ "$(id -u)" -eq 0 ] || APT="sudo apt-get"
    $APT update -qq >/dev/null 2>&1 || true
    $APT install -y -qq ffmpeg >/dev/null 2>&1 || true
  fi
  if ! command -v ffmpeg >/dev/null; then
    warn "apt failed; installing a pip-shipped static build"
    "$PYTHON" -m pip install -q imageio-ffmpeg
    FFMPEG="$("$PYTHON" -c 'import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())')"
    mkdir -p /usr/local/bin && ln -sf "$FFMPEG" /usr/local/bin/ffmpeg
  fi
  command -v ffmpeg >/dev/null && echo "    $(command -v ffmpeg)" || warn "ffmpeg missing: video will not render"
fi

# ---------------------------------------------------------------- packages
say "rivet"
"$PYTHON" -m pip install -q -e .

say "generative libraries"
"$PYTHON" -m pip install -q diffusers transformers accelerate safetensors soundfile kokoro huggingface_hub spacy

say "narration language model"
# Kokoro's grapheme-to-phoneme step fetches this at run time if it is absent, which
# breaks any offline or restricted-network run halfway through generation.
WHEEL="https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl"
"$PYTHON" -m pip install -q "en_core_web_sm@$WHEEL" 2>/dev/null \
  || "$PYTHON" -m pip install -q --trusted-host github.com --trusted-host objects.githubusercontent.com "en_core_web_sm@$WHEEL" \
  || warn "spaCy model not installed — narration will fail offline"

# ---------------------------------------------------------------- guard rail
AFTER="$("$PYTHON" -c 'import torch;print(torch.__version__)' 2>/dev/null || echo none)"
if [ "$BEFORE" != "none" ] && [ "$BEFORE" != "$AFTER" ]; then
  echo
  echo "    torch changed during install: $BEFORE -> $AFTER" >&2
  echo "    A PyPI build replaced the ROCm one; the GPU would silently disappear." >&2
  exit 1
fi

say "models"
"$PYTHON" scripts/models/fetch.py

say "ready"
cat <<EOF
    $PYTHON -m rivet --help          the CLI
    make offline-demo                 golden project, every socket blocked
    $PYTHON scripts/diversity.py      one campaign per demo brand
EOF
