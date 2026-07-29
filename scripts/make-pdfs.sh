#!/usr/bin/env bash
# Render the submission documents to PDF. Requires pandoc and a Chrome/Chromium binary.
set -euo pipefail

cd "$(dirname "$0")/.."

find_browser() {
  for candidate in \
    "${CHROME:-}" \
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
    "/Applications/Chromium.app/Contents/MacOS/Chromium" \
    "$(command -v google-chrome || true)" \
    "$(command -v google-chrome-stable || true)" \
    "$(command -v chromium || true)" \
    "$(command -v chromium-browser || true)"
  do
    if [ -n "$candidate" ] && [ -x "$candidate" ]; then
      printf '%s' "$candidate"
      return 0
    fi
  done
  return 1
}

if ! command -v pandoc >/dev/null; then
  echo "pandoc is required: brew install pandoc / apt install pandoc" >&2
  exit 1
fi

browser="$(find_browser)" || {
  echo "no Chrome or Chromium binary found; set CHROME=/path/to/chrome" >&2
  exit 1
}

render() {
  local src="$1" out="$2" title="$3"
  local html
  html="$(mktemp -t rivet-pdf).html"
  pandoc "$src" \
    --standalone \
    --embed-resources \
    --css scripts/pdf.css \
    --metadata title="$title" \
    -o "$html"
  "$browser" \
    --headless \
    --disable-gpu \
    --no-pdf-header-footer \
    --virtual-time-budget=4000 \
    --print-to-pdf="$out" \
    "$html" 2>/dev/null
  rm -f "$html"
  echo "wrote $out"
}

render docs/profile.md project-profile.pdf "Rivet — Project Profile"
if [ -f docs/poster.md ]; then
  render docs/poster.md poster.pdf "Rivet — Poster"
fi
