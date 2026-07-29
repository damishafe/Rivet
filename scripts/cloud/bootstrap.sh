#!/usr/bin/env bash
# Prepare a Radeon Cloud instance to run Rivet.
#
# The instance ships a ROCm build of PyTorch. Installing Rivet must never replace it:
# a PyPI torch would be the CPU or CUDA build and the GPU would silently disappear.
# So we install into a venv that can see the system packages, and verify torch is
# untouched afterwards.
set -euo pipefail

cd "$(dirname "$0")/../.."

say() { printf '\n=== %s ===\n' "$1"; }

torch_report() {
  python3 - <<'PY' 2>/dev/null || echo "none"
import torch
name = torch.cuda.get_device_name(0) if torch.cuda.is_available() else "no device"
hip = getattr(torch.version, "hip", None) or "n/a"
print(f"{torch.__version__}|{name}|hip {hip}")
PY
}

say "system torch before install"
BEFORE="$(torch_report)"
echo "  $BEFORE"
if [ "$BEFORE" = "none" ]; then
  echo "  no system torch found — this template is not a ROCm image" >&2
fi

say "ffmpeg"
if ! command -v ffmpeg >/dev/null; then
  echo "  installing ffmpeg"
  if ! command -v apt-get >/dev/null; then
    echo "  no apt-get; install ffmpeg manually" >&2
    exit 1
  fi
  APT=""
  if [ "$(id -u)" -eq 0 ]; then
    APT="apt-get"
  elif command -v sudo >/dev/null; then
    APT="sudo apt-get"
  else
    echo "  need root or sudo to install ffmpeg" >&2
    exit 1
  fi
  $APT update -qq
  $APT install -y -qq ffmpeg
fi
echo "  $(ffmpeg -version | head -1)"

say "python environment"
if ! command -v uv >/dev/null; then
  echo "  installing uv"
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
fi
uv venv --system-site-packages --allow-existing .venv
# shellcheck disable=SC1091
source .venv/bin/activate

say "model cache"
# Persistent storage keeps the weights between sessions; on metered hardware the
# second session should never pay for the same download twice.
# Prefer a mounted PVC: weights survive the instance and the next session skips
# the download. Fall back through the workspace to the home directory.
if [ -z "${MODEL_DIR:-}" ]; then
  for candidate in /persistent /workspace "$HOME"; do
    if [ -d "$candidate" ] && [ -w "$candidate" ]; then
      MODEL_DIR="$candidate/rivet-models"
      break
    fi
  done
  MODEL_DIR="${MODEL_DIR:-$HOME/rivet-models}"
fi
if ! mkdir -p "$MODEL_DIR/hub" 2>/dev/null; then
  MODEL_DIR="$HOME/rivet-models"
  mkdir -p "$MODEL_DIR/hub"
fi
case "$MODEL_DIR" in
  /persistent/*) echo "  persistent volume — a later session will reuse these weights" ;;
  *) echo "  NOT on a persistent volume — a new instance will download again" >&2 ;;
esac
export HF_HOME="$MODEL_DIR" HF_HUB_CACHE="$MODEL_DIR/hub"
if ! grep -q "RIVET_MODEL_CACHE" .venv/bin/activate 2>/dev/null; then
  {
    echo "# RIVET_MODEL_CACHE"
    echo "export HF_HOME=\"$MODEL_DIR\""
    echo "export HF_HUB_CACHE=\"$MODEL_DIR/hub\""
  } >>.venv/bin/activate
fi
echo "  $HF_HUB_CACHE"

say "rivet and generative libraries"
uv pip install -q -e .
uv pip install -q diffusers transformers accelerate safetensors soundfile kokoro huggingface_hub

say "system torch after install"
AFTER="$(torch_report)"
echo "  $AFTER"
if [ "$BEFORE" != "none" ] && [ "$BEFORE" != "$AFTER" ]; then
  echo "  torch changed during install — the ROCm build was replaced." >&2
  echo "  before: $BEFORE" >&2
  echo "  after:  $AFTER" >&2
  exit 1
fi

say "doctor"
rivet doctor

say "models"
python scripts/models/fetch.py

say "ready"
echo "  source .venv/bin/activate && ./scripts/cloud/evidence.sh"
