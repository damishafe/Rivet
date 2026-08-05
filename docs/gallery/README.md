# Rivet results gallery

Produced by `scripts/showcase.py` on **mps** (torch 2.13.0, hip n/a).

## Verified campaign

- receipt `ea72effef9454a4f`
- **passed: True**
- export pack: written

<img src="hero-hook.jpg" width="240">
<img src="hero-proof.jpg" width="240">
<img src="hero-cta.jpg" width="240">
<img src="hero-hook.jpg" width="240">
<img src="hero-hook.jpg" width="240">
<img src="hero-proof.jpg" width="240">
<img src="hero-proof.jpg" width="240">
<img src="hero-cta.jpg" width="240">
<img src="hero-cta.jpg" width="240">

[hero.mp4](hero.mp4)

## Tampered product asset

- receipt `36925ca927f0876a`
- **passed: False**
- export pack: withheld
- failing checks:
  - `hook` **A01** — mismatch
  - `proof` **A01** — mismatch
  - `cta` **A01** — mismatch
  - `hook` **A01** — mismatch
  - `hook` **A01** — mismatch
  - `proof` **A01** — mismatch
  - `proof` **A01** — mismatch
  - `cta` **A01** — mismatch
  - `cta` **A01** — mismatch

<img src="blocked-hook.jpg" width="240">
<img src="blocked-proof.jpg" width="240">
<img src="blocked-cta.jpg" width="240">
<img src="blocked-hook.jpg" width="240">
<img src="blocked-hook.jpg" width="240">
<img src="blocked-proof.jpg" width="240">
<img src="blocked-proof.jpg" width="240">
<img src="blocked-cta.jpg" width="240">
<img src="blocked-cta.jpg" width="240">

[blocked.mp4](blocked.mp4)

## One campaign, three delivery formats

The same scene as a vertical story, a square feed post and a wide banner. Each has its own
composition rather than a squashed crop, and each is audited separately — a legible story
does not smuggle through an illegible banner.

<img src="format-story.jpg" height="230">
<img src="format-feed.jpg" height="230">
<img src="format-banner.jpg" height="230">

Every export pack carries all nine stills, the assembled video, captions, the receipt and a
manifest hashing each member.
