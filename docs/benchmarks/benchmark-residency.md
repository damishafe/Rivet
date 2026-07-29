# Rivet benchmark

- fixture: `fixtures/kora-arc`
- generated: 2026-07-29T12:12:04+00:00
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
| resident | 16.8 | 41.2 | 58.0 | 9168 MB | 27/27 | 0 | `347606b58a93ba16` |
| reload-per-stage | 13.3 | 40.3 | 53.6 | 9165 MB | 27/27 | 0 | `347606b58a93ba16` |

**Determinism:** identical stills and audit observations across runs

**Measured total (2 run(s)):** median 55.78s, min 53.59s, max 57.98s (8.2% spread)

> Fewer than three measured runs: treat the total as indicative, not as a variance-bounded figure.

## Stages

### resident

| stage | seconds | peak VRAM | cache |
| --- | ---: | ---: | --- |
| segment | 0.08 | 8595 MB | miss |
| background.hook | 11.02 | 9168 MB | miss |
| composite.hook | 0.41 | 6800 MB | miss |
| background.proof | 3.29 | 9164 MB | miss |
| composite.proof | 0.59 | 6800 MB | miss |
| background.cta | 3.36 | 9164 MB | miss |
| composite.cta | 0.59 | 6800 MB | miss |
| motion.hook | 0.86 | 6800 MB | miss |
| narration.hook | 7.79 | 6800 MB | miss |
| motion.proof | 0.97 | 616 MB | miss |
| narration.proof | 3.44 | 756 MB | miss |
| motion.cta | 0.88 | 618 MB | miss |
| narration.cta | 3.03 | 737 MB | miss |

### reload-per-stage

| stage | seconds | peak VRAM | cache |
| --- | ---: | ---: | --- |
| segment | 0.08 | 76 MB | miss |
| background.hook | 7.23 | 9165 MB | miss |
| composite.hook | 0.42 | 76 MB | miss |
| background.proof | 7.22 | 9165 MB | miss |
| composite.proof | 0.59 | 76 MB | miss |
| background.cta | 7.40 | 9165 MB | miss |
| composite.cta | 0.59 | 76 MB | miss |
| motion.hook | 0.87 | 76 MB | miss |
| narration.hook | 3.12 | 731 MB | miss |
| motion.proof | 0.97 | 76 MB | miss |
| narration.proof | 3.23 | 757 MB | miss |
| motion.cta | 0.86 | 76 MB | miss |
| narration.cta | 3.19 | 733 MB | miss |
