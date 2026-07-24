import hashlib
import os
from pathlib import Path
from uuid import uuid4

from sqlalchemy.engine import Engine
from sqlmodel import Session, select

from rivet.domain.models import Asset, AssetRole, Provenance
from rivet.storage.records import AssetRow


def _atomic_write(dest: Path, data: bytes) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_name(f"{dest.name}.{uuid4().hex}.tmp")
    with open(tmp, "wb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp, dest)


class AssetStore:
    def __init__(self, engine: Engine, root: Path) -> None:
        self._engine = engine
        self._root = root

    def save(
        self,
        project_id: str,
        role: AssetRole,
        data: bytes,
        mime: str,
        suffix: str,
        width: int | None = None,
        height: int | None = None,
        provenance: Provenance = "original",
    ) -> Asset:
        digest = hashlib.sha256(data).hexdigest()
        dest = (
            self._root / "projects" / project_id / "assets" / digest[:2] / f"{digest}{suffix}"
        )
        if not dest.exists():
            _atomic_write(dest, data)
        asset = Asset(
            project_id=project_id,
            role=role,
            path=str(dest),
            sha256=digest,
            mime=mime,
            width=width,
            height=height,
            provenance=provenance,
        )
        with Session(self._engine) as session:
            session.add(
                AssetRow(id=asset.id, project_id=project_id, payload=asset.model_dump(mode="json"))
            )
            session.commit()
        return asset

    def get(self, asset_id: str) -> Asset | None:
        with Session(self._engine) as session:
            row = session.get(AssetRow, asset_id)
            return Asset.model_validate(row.payload) if row else None

    def find(self, project_id: str, role: AssetRole | None = None) -> list[Asset]:
        with Session(self._engine) as session:
            rows = session.exec(
                select(AssetRow).where(AssetRow.project_id == project_id)
            ).all()
        assets = [Asset.model_validate(row.payload) for row in rows]
        if role is not None:
            assets = [asset for asset in assets if asset.role == role]
        return sorted(assets, key=lambda asset: (asset.created_at, asset.id))
