# Rivet benchmark

- fixture: `fixtures/kora-arc`
- generated: 2026-07-29T12:24:27+00:00
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
| warmup | 17.4 | 43.5 | 60.9 | 9168 MB | 27/27 | 0 | `347606b58a93ba16` |
| resident | 13.4 | 28.4 | 41.8 | 9165 MB | 27/27 | 0 | `347606b58a93ba16` |
| reload-per-stage | 14.2 | 41.5 | 55.7 | 9165 MB | 27/27 | 0 | `347606b58a93ba16` |
| resident | 13.8 | 28.8 | 42.6 | 9165 MB | 27/27 | 0 | `347606b58a93ba16` |
| reload-per-stage | 13.5 | 42.5 | 56.0 | 9165 MB | 27/27 | 0 | `347606b58a93ba16` |

**Determinism:** identical stills and audit observations across runs

**Measured total (4 run(s)):** median 49.17s, min 41.76s, max 55.99s (34.1% spread)

## Model residency

| arm | runs | median total s |
| --- | ---: | ---: |
| resident | 2 | 42.2 |
| reload-per-stage | 2 | 55.8 |

Keeping one model resident is **13.7s faster** than reloading per stage. Arms alternate after a discarded warmup, so neither is advantaged by page-cache warmth.

## Stages

### warmup

| stage | seconds | peak VRAM | cache |
| --- | ---: | ---: | --- |
| segment | 0.08 | 8595 MB | miss |
| background.hook | 12.21 | 9168 MB | miss |
| composite.hook | 0.42 | 6800 MB | miss |
| background.proof | 3.27 | 9164 MB | miss |
| composite.proof | 0.60 | 6800 MB | miss |
| background.cta | 3.36 | 9164 MB | miss |
| composite.cta | 0.59 | 6800 MB | miss |
| motion.hook | 0.89 | 6800 MB | miss |
| narration.hook | 8.78 | 6800 MB | miss |
| motion.proof | 1.00 | 616 MB | miss |
| narration.proof | 3.36 | 756 MB | miss |
| motion.cta | 0.91 | 618 MB | miss |
| narration.cta | 3.07 | 737 MB | miss |

### resident

| stage | seconds | peak VRAM | cache |
| --- | ---: | ---: | --- |
| segment | 0.08 | 8596 MB | miss |
| background.hook | 8.10 | 9165 MB | miss |
| composite.hook | 0.42 | 6801 MB | miss |
| background.proof | 3.28 | 9165 MB | miss |
| composite.proof | 0.61 | 6801 MB | miss |
| background.cta | 3.37 | 9165 MB | miss |
| composite.cta | 0.61 | 6801 MB | miss |
| motion.hook | 0.90 | 6801 MB | miss |
| narration.hook | 3.46 | 6801 MB | miss |
| motion.proof | 0.94 | 617 MB | miss |
| narration.proof | 0.41 | 754 MB | miss |
| motion.cta | 0.91 | 618 MB | miss |
| narration.cta | 0.36 | 734 MB | miss |

### reload-per-stage

| stage | seconds | peak VRAM | cache |
| --- | ---: | ---: | --- |
| segment | 0.08 | 76 MB | miss |
| background.hook | 7.90 | 9165 MB | miss |
| composite.hook | 0.41 | 76 MB | miss |
| background.proof | 7.74 | 9165 MB | miss |
| composite.proof | 0.59 | 76 MB | miss |
| background.cta | 7.79 | 9165 MB | miss |
| composite.cta | 0.59 | 76 MB | miss |
| motion.hook | 0.87 | 76 MB | miss |
| narration.hook | 2.88 | 731 MB | miss |
| motion.proof | 0.99 | 76 MB | miss |
| narration.proof | 3.40 | 757 MB | miss |
| motion.cta | 0.90 | 76 MB | miss |
| narration.cta | 2.89 | 733 MB | miss |

### resident

| stage | seconds | peak VRAM | cache |
| --- | ---: | ---: | --- |
| segment | 0.08 | 8591 MB | miss |
| background.hook | 8.20 | 9165 MB | miss |
| composite.hook | 0.41 | 6801 MB | miss |
| background.proof | 3.29 | 9165 MB | miss |
| composite.proof | 0.59 | 6801 MB | miss |
| background.cta | 3.38 | 9165 MB | miss |
| composite.cta | 0.59 | 6801 MB | miss |
| motion.hook | 0.86 | 6801 MB | miss |
| narration.hook | 3.92 | 6801 MB | miss |
| motion.proof | 0.96 | 617 MB | miss |
| narration.proof | 0.41 | 754 MB | miss |
| motion.cta | 0.91 | 618 MB | miss |
| narration.cta | 0.36 | 734 MB | miss |

### reload-per-stage

| stage | seconds | peak VRAM | cache |
| --- | ---: | ---: | --- |
| segment | 0.08 | 76 MB | miss |
| background.hook | 7.82 | 9165 MB | miss |
| composite.hook | 0.42 | 76 MB | miss |
| background.proof | 7.75 | 9165 MB | miss |
| composite.proof | 0.60 | 76 MB | miss |
| background.cta | 7.83 | 9165 MB | miss |
| composite.cta | 0.59 | 76 MB | miss |
| motion.hook | 0.86 | 76 MB | miss |
| narration.hook | 3.15 | 731 MB | miss |
| motion.proof | 1.00 | 76 MB | miss |
| narration.proof | 3.72 | 757 MB | miss |
| motion.cta | 0.88 | 76 MB | miss |
| narration.cta | 3.26 | 733 MB | miss |
