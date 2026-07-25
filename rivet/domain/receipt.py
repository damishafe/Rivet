import hashlib
import json
from datetime import datetime

from pydantic import BaseModel, Field

from rivet.domain.models import AuditCheck, utcnow


class RepairRecord(BaseModel):
    shot_id: str
    kind: str
    before_passed: bool
    after_passed: bool
    detail: str


class SceneResult(BaseModel):
    shot_id: str
    still_path: str
    seed: int
    checks: list[AuditCheck]
    passed: bool


class CampaignReceipt(BaseModel):
    project_id: str
    created_at: datetime = Field(default_factory=utcnow)
    product_sha256: str
    logo_sha256: str
    scenes: list[SceneResult]
    repairs: list[RepairRecord] = Field(default_factory=list)
    video_path: str | None = None
    captions_path: str | None = None
    pack_path: str | None = None
    passed: bool
    receipt_hash: str = ""

    def finalize(self) -> "CampaignReceipt":
        payload = self.model_dump(
            mode="json", exclude={"receipt_hash", "created_at", "pack_path"}
        )
        digest = hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        return self.model_copy(update={"receipt_hash": digest})
