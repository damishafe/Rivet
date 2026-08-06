# Demo video script — 4 minutes

Record on the Radeon instance so the terminal shows the real device. Keep the browser and
a terminal side by side. Say the numbers out loud; a judge scoring "clear, stable and
diverse output" needs to hear the claim and see it land at the same moment.

Total: **4 min 20 s**. Aim for one take per section rather than one take overall.

---

## 0:00 – 0:25 · The problem

**On screen:** the landing page at `/`.

> "Someone selling handmade soap can generate fifty advertisements tonight. If one of them
> says 'clinically proven' — because a language model reached for a phrase that sounded
> like marketing — that's a fine they can't absorb. A large brand has a legal team between
> them and that mistake. They have a phone.
>
> Generative tools made advertising cheap. They didn't make *checking* it cheap. So the
> check stayed where it always was — with whoever could afford a reviewer.
>
> Rivet moves the check into the tool. The model is creative only where creativity is safe,
> every asset is audited as it's made, and one that fails is refused rather than shipped."

---

## 0:25 – 1:10 · One command, real hardware

**On screen:** terminal. Run `rivet doctor`.

> "Everything runs locally on one Radeon PRO W7900 — gfx1100, 48 gigabytes, ROCm 7.2."

Then start the campaign:

```bash
uv run rivet run $PID
```

Let the stage lines scroll — segment, three backgrounds, composites, motion, narration.

> "Segmentation, three SDXL backgrounds, compositing, motion, narration — and then the
> audit. Cold, this takes seventy-two seconds end to end. Forty-five with the models
> already resident."

**Do not speed this up.** The wait is the point: it is a real GPU doing real work.

---

## 1:10 – 1:55 · What the model was allowed to touch

**On screen:** the finished advertisement playing.

> "The background is generated. Everything else is not.
>
> The product is the photograph I supplied, cut out and composited afterwards. The logo is
> my file, placed by a recorded transform. The text is real typography from a bundled
> font — not glyphs a model guessed at.
>
> That is the whole design: the model never touches anything a brand would care about."

**Then the line that separates this from every other entry.** Deliver it slowly.

> "Compositing a logo deterministically is table stakes. Plenty of tools do that much.
>
> The question none of them answer is: *how do you know it worked?*
>
> So Rivet does the thing nobody else does. It checks its own output. And when a check
> fails, it refuses to export."

---

## 1:55 – 2:50 · The receipt, and the refusal

**On screen:** the Studio review screen, then switch to the tampered state.

> "Every scene passes ten checks — ninety across the nine we render. Not a score — named checks with observed values. The
> logo in this frame differs from my source file by 9.3 out of 255. The product by zero.
> Text contrast is 7.28 against a floor of four."

Open the receipt panel.

> "All of it lands in a Campaign Receipt: input hashes, seeds, per-stage timings, peak
> VRAM, every check. Hashed as one record."

**Now the moment.** Switch to the blocked state.

> "Here is the same advertisement — after I altered the product file behind the audit's
> back, once the brand had already approved it.
>
> A01 compares the approved sha256 against the bytes actually composited. Mismatch. The
> export is **refused**. No pack is written, and the project moves to `needs repair`.
>
> The advertisement looks fine. That is exactly the point — it looks fine, and it is
> still wrong, and the tool knows."

Pause for a beat here. This is the moment nobody else can show.

Say the word **refused** aloud, and let the screen sit on the withheld export for two full
seconds before moving on. A judge comparing entries side by side needs one image they can
recall: a finished-looking advertisement that this tool declined to ship.

---

## 2:50 – 3:25 · It is not tuned to one product

**On screen:** `docs/gallery/DIVERSITY.md`.

> "Same pipeline, three products: a speaker, an insulated flask, a coffee press.
> Different shapes, different palettes, different categories. Nothing is configured per
> brand — each palette is derived from its own logo.
>
> Running these actually found two bugs. Background prompts weren't conditioned on the
> brand palette, so a warm backdrop appeared behind a cold logo. And the audit caught it
> before I did."

---

## 3:25 – 3:50 · The check travels with the language

**On screen:** `docs/gallery/LANGUAGE-ZH.md` — the three Mandarin stills, then the refused set.

> "Same pipeline, run in Mandarin. The copy is written in Chinese, not translated. The
> narration is a Mandarin voice. The typography uses a font that carries the script, and
> the claims are audited as written.
>
> The first attempt passed every check and rendered every character as an empty box — the
> narrator spoke Chinese while the compositor reached for a Latin font. So I added a check
> for it. An advertisement nobody can read is now a refused export too."

---

## 3:50 – 4:20 · Evidence, and the close

**On screen:** terminal.

```bash
make offline-demo
```

> "One more thing. This is the whole pipeline with every outbound socket blocked at the
> Python layer. Ninety checks, a passing export, zero connection attempts. It is
> genuinely local.
>
> And it is reproducible: the benchmarks in this repository regenerate from a checked-in
> command, not from a screenshot. Including the one that says keeping a model resident is
> twenty-four percent faster — a result I had to throw away and re-measure, because the
> first version was measuring run order instead."

**Final frame:** the verified advertisement beside the refused one.

> "Other tools generate. Rivet generates, checks what it made, and refuses to ship what
> fails.
>
> Verified advertising on one Radeon GPU. The model gets to be creative. It doesn't get
> to be trusted."

---

## Recording notes

- **1920×1080, 30fps.** Terminal at a font size legible on a laptop — bump it two sizes
  past comfortable.
- **Do not cut the generation wait.** If you must compress, show a clock or say the elapsed
  time aloud; never imply it was faster than it was.
- The blocked-export moment at 1:55–2:50 is the section worth re-recording until it lands.
  Everything else is context.
- If narration is hard, record picture first and voice over afterwards — but keep the
  terminal output real and uncut.
