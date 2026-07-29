# Rivet benchmark

- fixture: `fixtures/kora-arc`
- generated: 2026-07-29T12:10:15+00:00
- accelerator: AMD Radeon Graphics
- cuda: n/a
- device: cuda
- hip: 7.2.53211-e1a6bc5663
- torch: 2.9.1+gitff65f5b
- total_vram_mb: 49136
- vram_metric: torch.cuda.max_memory_allocated, peak reset before each stage

## Runs

| mode | plan s | campaign s | total s | peak VRAM | checks | repairs | content |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| warmup | 17.2 | 41.4 | 58.6 | 9168 MB | 27/27 | 0 | `347606b58a93ba16` |
| hot | 13.3 | 27.9 | 41.2 | 9165 MB | 27/27 | 0 | `347606b58a93ba16` |

**Determinism:** identical stills and audit observations across runs

**Measured total (1 run(s)):** median 41.2s, min 41.2s, max 41.2s (0.0% spread)

> Fewer than three measured runs: treat the total as indicative, not as a variance-bounded figure.

## Stages

### warmup

| stage | seconds | peak VRAM | cache |
| --- | ---: | ---: | --- |
| segment | 0.08 | 8595 MB | miss |
| background.hook | 11.46 | 9168 MB | miss |
| composite.hook | 0.42 | 6800 MB | miss |
| background.proof | 3.27 | 9164 MB | miss |
| composite.proof | 0.60 | 6800 MB | miss |
| background.cta | 3.37 | 9164 MB | miss |
| composite.cta | 0.59 | 6800 MB | miss |
| motion.hook | 0.93 | 6800 MB | miss |
| narration.hook | 7.70 | 6800 MB | miss |
| motion.proof | 0.98 | 616 MB | miss |
| narration.proof | 3.27 | 756 MB | miss |
| motion.cta | 0.90 | 618 MB | miss |
| narration.cta | 2.99 | 737 MB | miss |

### hot

| stage | seconds | peak VRAM | cache |
| --- | ---: | ---: | --- |
| segment | 0.08 | 8596 MB | miss |
| background.hook | 7.65 | 9165 MB | miss |
| composite.hook | 0.42 | 6801 MB | miss |
| background.proof | 3.32 | 9165 MB | miss |
| composite.proof | 0.59 | 6801 MB | miss |
| background.cta | 3.40 | 9165 MB | miss |
| composite.cta | 0.59 | 6801 MB | miss |
| motion.hook | 0.87 | 6801 MB | miss |
| narration.hook | 3.52 | 6801 MB | miss |
| motion.proof | 0.96 | 617 MB | miss |
| narration.proof | 0.41 | 754 MB | miss |
| motion.cta | 0.88 | 618 MB | miss |
| narration.cta | 0.36 | 734 MB | miss |
