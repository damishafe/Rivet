import hashlib
from dataclasses import dataclass, field
from pathlib import Path

from sqlalchemy.engine import Engine

from rivet.adapters.background import BackgroundStage
from rivet.adapters.composite import CompositeStage
from rivet.adapters.motion import MotionStage
from rivet.adapters.narrate import NarrateStage
from rivet.adapters.segment import SegmentStage
from rivet.domain.models import Asset, BrandDNA, PaletteColor, Project, ShotPlan
from rivet.domain.states import ProjectStatus
from rivet.pipeline.runner import PlannedStage
from rivet.pipeline.stage import Stage, StageRequest
from rivet.storage.assets import AssetStore
from rivet.storage.plans import PlanStore
from rivet.storage.projects import ProjectStore

Color = tuple[int, int, int]


class CampaignNotFound(Exception):
    pass


class CampaignConflict(Exception):
    pass


class CampaignFailed(Exception):
    pass


@dataclass
class CampaignStages:
    segment: Stage = field(default_factory=SegmentStage)
    background: Stage = field(default_factory=BackgroundStage)
    narrate: Stage = field(default_factory=NarrateStage)
    composite: Stage = field(default_factory=CompositeStage)
    motion: Stage = field(default_factory=MotionStage)


@dataclass
class CampaignInputs:
    project: Project
    shots: list[ShotPlan]
    brand: BrandDNA
    product: Asset
    logo: Asset


def sha256_file(path: str) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def accent_rgb(palette: list[PaletteColor]) -> Color:
    if not palette:
        return (255, 59, 0)
    value = palette[0].hex.lstrip("#")
    return (int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16))


def resolve_campaign_inputs(engine: Engine, asset_root: Path, project_id: str) -> CampaignInputs:
    projects = ProjectStore(engine)
    project = projects.get(project_id)
    if project is None:
        raise CampaignNotFound("project not found")
    if project.status != ProjectStatus.PLANNED:
        raise CampaignConflict("campaign requires a planned project")
    shots = PlanStore(engine).get_plan(project_id)
    if shots is None:
        raise CampaignConflict("no storyboard plan")
    brand = projects.get_brand_dna(project_id)
    if brand is None or brand.confirmed_at is None:
        raise CampaignConflict("confirmed brand dna required")
    assets = AssetStore(engine, asset_root)
    product = assets.get(brand.product_asset_id)
    logo = assets.get(brand.logo_asset_id)
    if product is None or logo is None:
        raise CampaignConflict("confirmed product and logo assets missing")
    return CampaignInputs(project=project, shots=shots, brand=brand, product=product, logo=logo)


def generation_plan(
    inputs: CampaignInputs, stages: CampaignStages, workdir: Path, accent: Color
) -> list[PlannedStage]:
    cutout_path = str(workdir / "cutout.png")
    plan = [
        PlannedStage(
            stage=stages.segment,
            request=StageRequest(
                stage="segment",
                seed=inputs.project.campaign_seed,
                config={"image_path": inputs.product.path},
            ),
        )
    ]
    for shot in inputs.shots:
        plan.append(
            PlannedStage(
                stage=stages.background,
                request=StageRequest(
                    stage=f"background.{shot.shot_id}", seed=shot.seed,
                    config={
                        "shot_id": shot.shot_id,
                        "prompt": shot.background_prompt,
                        "negative_prompt": shot.negative_prompt,
                    },
                ),
            )
        )
        plan.append(
            PlannedStage(
                stage=stages.composite,
                request=StageRequest(
                    stage=f"composite.{shot.shot_id}", seed=shot.seed,
                    config={
                        "background_path": str(workdir / f"{shot.shot_id}.png"),
                        "cutout_path": cutout_path,
                        "logo_path": inputs.logo.path,
                        "layout": shot.layout_template,
                        "shot_id": shot.shot_id,
                        "headline": shot.copy_.headline,
                        "support": shot.copy_.support,
                        "cta": shot.copy_.cta,
                        "accent": list(accent),
                    },
                ),
            )
        )
    return plan
