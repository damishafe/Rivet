# Rivet

## Verified multimodal ad creation on one AMD Radeon GPU

**AMD AI DevMaster Hackathon 2026 · Track 1 · Radeon PRO W7900 · ROCm 7.2**

---

## The problem

A brand can generate a thousand advertisements in an afternoon and ship none of them.

Not because the quality is poor — because a generative model redraws whatever it is given. It bends
the logo, invents a button the product does not have, and renders text as plausible glyphs that
spell nothing. Marketing cannot show that to customers. Legal cannot approve it. So the output goes
back to a designer to rebuild by hand, and the generative step has saved nobody any time.

The usual answer is to ask for trust: better prompts, better models, a human at the end. Review does
not scale to a thousand assets, and trust is not evidence.

---

## What Rivet does

A product photo, a brand kit and a short brief become a **verified three-scene vertical
advertisement** — on one Radeon GPU, with no network access.

**The model generates the background, and nothing else.** The product cutout, the logo and every
character of text are composited afterwards, deterministically, from the original files. This is
structural rather than advisory: the compositor reads the source assets directly, and the audit
proves what landed in the frame is pixel-identical to what came in.

**Every export carries a Campaign Receipt** — input hashes, seeds, per-stage wall time, peak VRAM,
every check with its observed value, and any repair applied. A pack ships with a manifest hashing
every file in it.

---

## Ten checks on every scene

| | verifies |
|---|---|
| **A01** | product and logo match the brand-confirmed assets, by sha256 |
| **A02** | the logo in the frame is the real logo, pixel for pixel |
| **A03** | rendered copy equals approved copy |
| **A04** | the background stays on-brand |
| **A05** | safe-area geometry, and that no text overflowed |
| **A06** | the product occupies enough of the frame |
| **A07** | no forbidden claims, all required phrases — including narration |
| **A09** | the product in the frame is the real product, pixel for pixel |
| **A10** | text is legible against what is actually behind it |
| **A11** | every character rendered exists in the font that drew it |
| **A08** | *advisory* — semantic fit judged by Qwen3-VL, never blocks |

If a deterministic check fails, **no pack is written**. The project moves to `needs_repair`.
When a claims check fails, Rivet rewrites the offending copy, recomposites, re-audits and records
what changed — and the audit runs *before* the video is rendered, so the film is built from the
repaired frames rather than certified separately from them.

---

## Measured on the Radeon PRO W7900

gfx1100 · 49136 MB · ROCm 7.2.53211 · PyTorch 2.9.1

| | seconds | audit |
|---|---:|---|
| **Cold** — plan, generate, audit, render, pack | **71.7** | 90/90 |
| **Hot** — models already resident | **45.4** | 90/90 |
| **Offline** — every outbound socket blocked | — | **90/90**, 0 outbound attempts |

**Peak VRAM 9168 MB of 49136.** One heavy model is held at a time; 81% of the card stays free.

### Model residency — the optimisation

SDXL rebuilt its pipeline and VAE from disk for every scene. Heavy models now pass through a
residency scheduler: acquiring a different model releases the previous one first, so exactly one is
resident and the VRAM headroom rule holds by construction.

| arm | median total |
|---|---:|
| **resident** | **42.2s** |
| reload per stage | 55.8s |

**13.7s faster — 24% end to end, 32% on generation.** Arms alternate after a discarded warmup: an
unalternated pair hands the second arm a warm page cache worth ~17s, more than the effect itself.
The first attempt reported residency as *slower*; it was measuring run order and was discarded.

### Determinism

One content digest — `347606b58a93ba16` — across **all eleven runs**, including both residency arms.
It covers rendered pixels, seeds and audit observations, so only identical output satisfies it.

---

## Reproduce it

```bash
uv sync --extra gpu
make offline-demo     # passing export, network blocked
make test-golden      # byte-identical compositing
uv run rivet benchmark --fixture fixtures/kora-arc --mode residency
```

Every number here is produced by these commands. Nothing is quoted from a private session.

---

**Qwen3-VL-4B** plans · **SDXL** backgrounds · **SAM 2.1** cutout · **Kokoro-82M** narration ·
**Whisper** brief · deterministic Python composites, audits and signs.
