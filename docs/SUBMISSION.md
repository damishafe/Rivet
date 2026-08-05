# Track 1, TEAM_NAME, Rivet

**Verified multimodal ad creation on one AMD Radeon GPU.**

Someone selling handmade soap can generate fifty advertisements tonight. If one says
"clinically proven" because a language model reached for a phrase that sounded like
marketing, that is a fine they cannot absorb — and unlike a large brand, there is no legal
team between them and it. Generative tools made advertising cheap without making *checking*
it cheap.

Rivet moves the check into the tool. A product image, brand kit and brief become a
three-scene advertisement in three delivery formats, with narration and captions. The
product, logo and typography never pass through a generative model. Every asset is audited
as it is made, every export carries a Campaign Receipt, and one that fails is refused
rather than shipped.

## Deliverables

| Requirement | Artifact |
|---|---|
| Project Profile Document (PDF) | [`project-profile.pdf`](project-profile.pdf) — source: [`docs/profile.md`](docs/profile.md) |
| Project source code | this repository |
| README with environment, startup, dependencies | [`README.md`](README.md) · one-command setup: [`install.sh`](install.sh) |
| Demo video (3–5 min) | DEMO_VIDEO_LINK |
| Supplementary material | [`poster.pdf`](poster.pdf) |
| Live studio (no install) | **https://rivet-amd.vercel.app** |

## Verified execution on the Radeon PRO W7900

Produced by the checked-in commands on the contest hardware, not quoted from a private
session. Raw logs in [`docs/evidence/`](docs/evidence/), reports in
[`docs/benchmarks/`](docs/benchmarks/).

- Device: `AMD Radeon Graphics` · `gfx1100` · **49136 MB**
- Stack: ROCm `7.2.53211-e1a6bc5663` · PyTorch `2.9.1+gitff65f5b`
- SDXL attention runs through ROCm's AOTriton efficient-attention path

| Measurement | Result |
|---|---|
| Full campaign, cold | **67.8 s** — plan, generate, audit, render, pack |
| Same work, models resident | **41.2 s** |
| Deterministic checks | **27 / 27** across three scenes |
| Peak VRAM | **9168 MB** of 49136 (81% of the card free) |
| Offline gate, every outbound socket blocked | **passes**, 0 connection attempts |
| Determinism | one content digest `347606b58a93ba16` across 11 runs |
| Model residency optimisation | **13.7 s faster, 24% end to end** |

Reproduce:

```bash
./install.sh
make offline-demo                                    # gate G2: no network, passing export
make test-golden                                     # byte-identical compositing
uv run rivet benchmark --fixture fixtures/kora-arc --mode residency
```

## What makes it different

Most generative ad tools ask you to trust the output. Rivet proves it.

**Protected layers never pass through a generative model.** The model generates the
background and nothing else. The product cutout, the logo and every character of text are
composited afterwards from the original files. The audit then verifies that what landed in
the frame is pixel-identical to what came in.

**Ten checks gate every scene.** Nine are deterministic and block the export; one is
advisory.

| | Verifies |
|---|---|
| A01 | product and logo match the brand-confirmed assets, by sha256 |
| A02 | the logo in the frame matches the source, pixel for pixel |
| A03 | rendered copy equals approved copy |
| A04 | background colour stays on-brand |
| A05 | safe-area geometry, and that no text overflowed its box |
| A06 | the product occupies enough of the frame |
| A07 | no forbidden claims, all required phrases — including spoken narration |
| A09 | the product in the frame matches the cutout, pixel for pixel |
| A10 | text contrast is legible against what is actually behind it |
| A08 | *(advisory)* semantic fit, judged by Qwen3-VL |

**A failing export is refused.** [`docs/gallery/`](docs/gallery/) shows a verified campaign
beside the same advertisement after the product file was altered post-approval: A01 detects
the mismatch, the project moves to `needs_repair`, and no pack is written.

**One campaign, three delivery formats.** A 9:16 story, a 1:1 feed post and a 16:9 banner,
each with its own composition rather than a squashed crop, and **each audited separately** —
so a legible story cannot smuggle through an illegible banner. Nine audited deliverables
from one run.

**One pipeline, three brands.** [`docs/gallery/DIVERSITY.md`](docs/gallery/DIVERSITY.md)
runs a speaker, an insulated flask and a coffee press through the same code with nothing
configured per brand — each palette is derived from its own logo.

## Models

All open-source, pinned to exact revisions in
[`MODEL_LICENSES.md`](MODEL_LICENSES.md), all running locally on the Radeon.

SDXL 1.0 (backgrounds) · Qwen3-VL-4B (planning and the advisory audit) · SAM 2.1 (product
cutout) · Kokoro-82M (narration) · Whisper (spoken brief). Compositing, audit and receipt
are deterministic Python with no model involved.

## What we do not claim

- The advisory semantic check (A08) is Qwen's judgement and never blocks an export.
- A03 compares rendered copy against approved copy as metadata; it is not OCR of the frame.
- The residency comparison alternates its arms after a discarded warmup. An earlier
  unalternated run reported the optimisation as *slower*; that result measured run order
  and was discarded rather than published.
- Peak VRAM is reported only where a true per-stage counter exists. On hardware without
  one the reports print `n/a` rather than a process-wide figure.
