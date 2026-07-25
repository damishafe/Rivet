import json
import zipfile
from pathlib import Path

import pytest
from PIL import Image

from rivet.domain.models import AuditCheck
from rivet.domain.receipt import CampaignReceipt, SceneResult
from rivet.render.pack import build_pack


def _checks() -> list[AuditCheck]:
    return [
        AuditCheck(
            check_id="A01", metric="m", threshold="t", observed="o", passed=True, owner_stage="s"
        )
    ]


def test_pack_bundles_files_and_manifest(tmp_path: Path) -> None:
    workdir = tmp_path / "work"
    workdir.mkdir()
    video = workdir / "campaign.mp4"
    video.write_bytes(b"fake video bytes")
    srt = workdir / "campaign.srt"
    srt.write_text("1\n00:00:00,000 --> 00:00:04,000\nKora Arc\n")
    still = workdir / "hook-still.png"
    Image.new("RGB", (16, 16), (30, 30, 30)).save(still)
    receipt = CampaignReceipt(
        project_id="p1",
        product_sha256="a" * 64,
        logo_sha256="b" * 64,
        scenes=[SceneResult(shot_id="hook", still_path=str(still), seed=1, checks=_checks(), passed=True)],
        video_path=str(video),
        captions_path=str(srt),
        passed=True,
    ).finalize()

    out = workdir / "pack.zip"
    build_pack(workdir, receipt, out)
    assert out.exists()
    with zipfile.ZipFile(out) as archive:
        names = set(archive.namelist())
        assert {"campaign.mp4", "campaign.srt", "hook-still.png", "receipt.json", "manifest.json"} <= names
        manifest = json.loads(archive.read("manifest.json"))
        assert manifest["passed"] is True
        assert manifest["receipt_hash"] == receipt.receipt_hash
        assert all(len(entry["sha256"]) == 64 for entry in manifest["files"])
        assert {entry["name"] for entry in manifest["files"]} == {
            "receipt.json", "campaign.mp4", "campaign.srt", "hook-still.png",
        }


def test_pack_raises_when_referenced_evidence_missing(tmp_path: Path) -> None:
    workdir = tmp_path / "work"
    workdir.mkdir()
    receipt = CampaignReceipt(
        project_id="p1",
        product_sha256="a" * 64,
        logo_sha256="b" * 64,
        scenes=[
            SceneResult(
                shot_id="hook", still_path=str(workdir / "gone.png"), seed=1,
                checks=_checks(), passed=True,
            )
        ],
        passed=True,
    ).finalize()
    with pytest.raises(FileNotFoundError):
        build_pack(workdir, receipt, workdir / "pack.zip")
