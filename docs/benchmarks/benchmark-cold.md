# Rivet benchmark

- fixture: `fixtures/kora-arc`
- generated: 2026-07-29T12:08:59+00:00
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
| cold | 17.3 | 50.5 | 67.8 | 9168 MB | 27/27 | 0 | `347606b58a93ba16` |

**Determinism:** not verified

**Measured total (1 run(s)):** median 67.83s, min 67.83s, max 67.83s (0.0% spread)

> Fewer than three measured runs: treat the total as indicative, not as a variance-bounded figure.

## Stages

### cold

| stage | seconds | peak VRAM | cache |
| --- | ---: | ---: | --- |
| segment | 0.08 | 8595 MB | miss |
| background.hook | 11.59 | 9168 MB | miss |
| composite.hook | 0.41 | 6800 MB | miss |
| background.proof | 3.29 | 9164 MB | miss |
| composite.proof | 0.59 | 6800 MB | miss |
| background.cta | 3.36 | 9164 MB | miss |
| composite.cta | 0.59 | 6800 MB | miss |
| motion.hook | 0.89 | 6800 MB | miss |
| narration.hook | 10.44 | 6800 MB | miss |
| motion.proof | 0.96 | 616 MB | miss |
| narration.proof | 6.63 | 756 MB | miss |
| motion.cta | 0.93 | 618 MB | miss |
| narration.cta | 5.92 | 737 MB | miss |
