from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from rivet.domain.ids import new_id
from rivet.domain.states import ProjectStatus


def utcnow() -> datetime:
    return datetime.now(UTC)


class PaletteColor(BaseModel):
    hex: str = Field(pattern=r"^#[0-9a-fA-F]{6}$")
    role: str


class ApprovedFact(BaseModel):
    claim: str
    source: str


class BrandDNA(BaseModel):
    product_name: str
    palette: list[PaletteColor]
    tone: list[str]
    audience: str
    required_text: list[str]
    forbidden_claims: list[str]
    approved_facts: list[ApprovedFact] = []
    logo_asset_id: str
    product_asset_id: str
    confirmed_at: datetime | None = None


class ShotCopy(BaseModel):
    headline: str
    support: str
    cta: str


class ProductPlacement(BaseModel):
    anchor: str
    scale: float = Field(gt=0, le=1)
    rotation: float = 0.0
    min_visible_area: float = Field(gt=0, le=1)


class LogoPlacement(BaseModel):
    anchor: str
    scale: float = Field(gt=0, le=1)


class Motion(BaseModel):
    mode: Literal["i2v", "controlled"]
    camera: str
    intensity: float = Field(ge=0, le=1)


class ShotPlan(BaseModel):
    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    shot_id: Literal["hook", "proof", "cta"]
    purpose: str
    duration_s: float = Field(gt=0)
    background_prompt: str
    negative_prompt: str = ""
    copy_: ShotCopy = Field(alias="copy", serialization_alias="copy")
    product: ProductPlacement
    logo: LogoPlacement
    layout_template: str
    motion: Motion
    narration: str
    seed: int


class PlanValidationError(ValueError):
    pass


def validate_plan(shots: list[ShotPlan]) -> None:
    ids = [shot.shot_id for shot in shots]
    if ids != ["hook", "proof", "cta"]:
        raise PlanValidationError("plan must contain exactly hook, proof, cta in order")
    total = sum(shot.duration_s for shot in shots)
    if not 12 <= total <= 15:
        raise PlanValidationError(f"total duration {total}s outside the 12-15s window")


AssetRole = Literal["product", "logo", "brief_audio", "style_ref", "derived"]


class Project(BaseModel):
    id: str = Field(default_factory=new_id)
    name: str = Field(min_length=1, max_length=120)
    status: ProjectStatus = ProjectStatus.DRAFT
    campaign_seed: int
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)
    active_version: int = 1


class Asset(BaseModel):
    id: str = Field(default_factory=new_id)
    project_id: str
    role: AssetRole
    path: str
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    mime: str
    width: int | None = None
    height: int | None = None
    provenance: Literal["original", "derived"] = "original"


class StageRun(BaseModel):
    id: str = Field(default_factory=new_id)
    project_id: str
    stage: str
    model: str | None = None
    revision: str | None = None
    dtype: str | None = None
    seed: int
    started_at: datetime
    finished_at: datetime | None = None
    peak_vram_mb: int | None = None
    status: Literal["running", "succeeded", "failed", "cancelled"]
    fallback_used: bool = False
    cache_hit: bool = False


class AuditCheck(BaseModel):
    check_id: str
    metric: str
    threshold: float | str
    observed: float | str
    passed: bool
    evidence_path: str | None = None
    owner_stage: str


class Export(BaseModel):
    id: str = Field(default_factory=new_id)
    project_id: str
    version: int
    outputs: dict[str, str]
    manifest_hash: str
    receipt_hash: str
    created_at: datetime = Field(default_factory=utcnow)
