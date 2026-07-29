# Model, font and asset licenses

Every model, font, music track and demo asset shipped or downloaded by Rivet is recorded here with its exact revision and license before feature freeze (NFR-09). Nothing enters the pipeline until its row exists.

Revisions are the commit hashes Rivet resolves from the local Hugging Face snapshot at run time, so a
reader can confirm that the weights used are the weights recorded here. No weights are committed to
this repository; `make offline-demo` proves the pipeline runs from the local cache with the network
blocked.

`rivet submission-check` fails if any model referenced in the source is missing from this table.

## Models

| Kind | Name | Revision | License | Notes |
|----|----|----|----|----|
| Diffusion | `stabilityai/stable-diffusion-xl-base-1.0` | `462165984030d82259a11f4367a4eed129e94a7b` | CreativeML Open RAIL++-M | scene backgrounds only; never renders the product, logo or text |
| VAE | `madebyollin/sdxl-vae-fp16-fix` | `207b116dae70ace3637169f1ddd2434b91b3a8cd` | MIT | fp16-safe VAE for the SDXL pipeline |
| Vision-language | `Qwen/Qwen3-VL-4B-Instruct` | `ebb281ec70b05090aa6165b016eac8ec08e71b17` | Apache 2.0 | scene planning and the advisory A08 semantic audit |
| Segmentation | `facebook/sam2.1-hiera-small` | `ee5bba1d82bb8749febdf90f45e84b687142ba03` | Apache 2.0 | product cutout when the source image needs segmenting |
| Speech synthesis | `hexgrad/Kokoro-82M` | `f3ff3571791e39611d31c381e3a41a3af07b4987` | Apache 2.0 | scene narration |
| Speech recognition | `openai/whisper-tiny.en` | `87c7102498dcde7456f24cfd30239ca606ed9063` | MIT | transcribes the spoken brief |
| Linguistic model | `en_core_web_sm` (spaCy) | `3.8.0` | MIT | grapheme-to-phoneme for narration; pinned in `pyproject.toml` because Kokoro otherwise downloads it mid-generation |

## Fonts

| Kind | Name | Revision | License | Notes |
|----|----|----|----|----|
| Font | Inter (variable) | Inter 4.x (opsz,wght variable) | SIL OFL 1.1 | bundled in `rivet/compositor/fonts/` for deterministic ad typography |
| Font | Space Grotesk, Inter, JetBrains Mono | `@fontsource/*` pinned in `apps/web/package-lock.json` | SIL OFL 1.1 | self-hosted web UI typography; no CDN requests |

## Demo assets

| Kind | Name | Origin | License | Notes |
|----|----|----|----|----|
| Brand | Kora Arc | created for this project | project license | fictional brand; name, palette, copy and logo are original and reference no real company |
| Image | `fixtures/kora-arc/product.png` | created for this project | project license | synthetic product rendering |
| Image | `fixtures/kora-arc/logo.png` | created for this project | project license | original wordmark |

No music track is shipped. If one is added, its row lands here before it enters the pipeline.
