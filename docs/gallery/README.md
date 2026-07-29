# Rivet results gallery

Produced by `scripts/showcase.py` on **AMD Radeon Graphics** (torch 2.9.1+gitff65f5b, hip 7.2.53211-e1a6bc5663).

Two of the three scenes are shown for each run; the full set ships in the export pack.

## Verified campaign

- receipt `c6914739cccdd9cb`
- **passed: True**
- export pack: written

<img src="hero-hook.jpg" width="240">
<img src="hero-cta.jpg" width="240">


## Tampered product asset

- receipt `e5ca454919385062`
- **passed: False**
- export pack: withheld
- failing checks:
  - `hook` **A01** — mismatch
  - `proof` **A01** — mismatch
  - `cta` **A01** — mismatch

<img src="blocked-hook.jpg" width="240">
<img src="blocked-cta.jpg" width="240">


Full-resolution stills, the assembled video, the receipt and a manifest hashing every member ship inside each campaign's export pack.