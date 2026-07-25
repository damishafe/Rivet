import hashlib
import json
import zipfile
from pathlib import Path

from rivet.domain.receipt import CampaignReceipt


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_pack(workdir: Path, receipt: CampaignReceipt, out_path: Path) -> None:
    receipt_file = workdir / "receipt.json"
    receipt_file.write_text(receipt.model_dump_json(indent=2))

    members: list[Path] = [receipt_file]
    if receipt.video_path:
        members.append(Path(receipt.video_path))
    if receipt.captions_path:
        members.append(Path(receipt.captions_path))
    members.extend(Path(scene.still_path) for scene in receipt.scenes)
    members = [path for path in members if path.exists()]

    manifest = {
        "project_id": receipt.project_id,
        "passed": receipt.passed,
        "receipt_hash": receipt.receipt_hash,
        "files": [
            {"name": path.name, "sha256": _sha256(path), "size": path.stat().st_size}
            for path in members
        ],
    }
    manifest_file = workdir / "manifest.json"
    manifest_file.write_text(json.dumps(manifest, indent=2))
    members.append(manifest_file)

    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in members:
            archive.write(path, path.name)
