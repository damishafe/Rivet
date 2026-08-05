"""Run one verified campaign per brand, to show the pipeline is not tuned to one product.

Each brand has a different silhouette, palette and category. The brand palette is
derived from its own logo, so the backgrounds, accents and typography differ per run
without any per-brand configuration.
"""

import argparse
import asyncio
import json
import shutil
import sys
from pathlib import Path

from rivet.pipeline.bootstrap import confirm_brand, derive_plan, ingest_asset
from rivet.pipeline.campaign import run_campaign
from rivet.storage.assets import AssetStore
from rivet.storage.db import make_engine
from rivet.storage.projects import ProjectStore
from rivet.telemetry.vram import accelerator_report

BRANDS = (
    ("kora-arc", "Kora Arc", "a portable speaker for campus creators who record anywhere"),
    ("lumen-flask", "Lumen", "an insulated water bottle for commuters who hate lukewarm coffee"),
    ("terra-press", "Terra", "a manual coffee press for people who make one good cup a day"),
)
GALLERY = Path("docs/gallery")
SEED = 7


def run_brand(root: Path, slug: str, name: str, brief: str, vlm: bool) -> dict[str, object]:
    fixture = Path("fixtures") / slug
    engine = make_engine(root / "rivet.db")
    projects = ProjectStore(engine)
    assets = AssetStore(engine, root)
    project = projects.create(name, campaign_seed=SEED)
    product = ingest_asset(assets, project.id, fixture / "product.png", "product")
    logo = ingest_asset(assets, project.id, fixture / "logo.png", "logo")
    confirm_brand(engine, root, project.id, product, logo)
    projects.set_brief(project.id, brief)
    derive_plan(engine, project.id, product.path, use_vlm=vlm)
    receipt = asyncio.run(run_campaign(engine, root, project.id, semantic=False))
    data = json.loads(receipt.model_dump_json())

    GALLERY.mkdir(parents=True, exist_ok=True)
    stills: list[str] = []
    for scene in data["scenes"]:
        if scene.get("format", "story") != "story":
            continue
        src = Path(scene["still_path"])
        if src.is_file():
            dest = GALLERY / f"brand-{slug}-{scene['shot_id']}.png"
            shutil.copy2(src, dest)
            stills.append(dest.name)
    checks = [c for s in data["scenes"] for c in s["checks"]]
    return {
        "slug": slug,
        "name": name,
        "passed": data["passed"],
        "receipt": data["receipt_hash"][:16],
        "checks": f"{sum(1 for c in checks if c['passed'])}/{len(checks)}",
        "headlines": [s["shot_id"] for s in data["scenes"]],
        "copy": [
            next(iter([c["observed"] for c in s["checks"] if c["check_id"] == "A03"]), "")
            for s in data["scenes"]
        ],
        "stills": stills,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workdir", type=Path, default=Path(".diversity"))
    parser.add_argument("--no-vlm", dest="vlm", action="store_false")
    args = parser.parse_args()

    shutil.rmtree(args.workdir, ignore_errors=True)
    results = []
    for index, (slug, name, brief) in enumerate(BRANDS, start=1):
        print(f"{index}/{len(BRANDS)} {name} ...", flush=True)
        result = run_brand(args.workdir / slug, slug, name, brief, args.vlm)
        results.append(result)
        print(f"    passed={result['passed']} checks={result['checks']}")

    env = accelerator_report()
    where = env.get("accelerator") or env.get("device", "unknown")
    lines = [
        "# One pipeline, three brands",
        "",
        (
            f"Produced by `scripts/diversity.py` on **{where}** "
            f"(torch {env.get('torch', 'n/a')}, hip {env.get('hip', 'n/a')})."
        ),
        "",
        "Nothing is configured per brand. The palette is derived from each logo, the copy and",
        "background prompts are written per product, and the same ten checks gate every scene.",
        "",
        "| Brand | Verdict | Checks | Receipt |",
        "| --- | --- | ---: | --- |",
    ]
    for r in results:
        verdict = "verified" if r["passed"] else "blocked"
        lines.append(f"| {r['name']} | {verdict} | {r['checks']} | `{r['receipt']}` |")
    lines.append("")
    for r in results:
        lines += [f"### {r['name']}", ""]
        lines += [f'<img src="{s}" width="200">' for s in r["stills"]]
        lines.append("")
    (GALLERY / "DIVERSITY.md").write_text("\n".join(lines))
    print(f"wrote {GALLERY}/DIVERSITY.md")
    return 0 if all(r["passed"] for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
