from enum import StrEnum


class ProjectStatus(StrEnum):
    DRAFT = "draft"
    BRAND_READY = "brand_ready"
    PLANNED = "planned"
    GENERATING = "generating"
    COMPOSED = "composed"
    AUDITING = "auditing"
    NEEDS_REPAIR = "needs_repair"
    READY = "ready"
    EXPORTED = "exported"
    FAILED = "failed"
    CANCELLED = "cancelled"


TRANSITIONS: dict[ProjectStatus, frozenset[ProjectStatus]] = {
    ProjectStatus.DRAFT: frozenset({ProjectStatus.BRAND_READY}),
    ProjectStatus.BRAND_READY: frozenset({ProjectStatus.PLANNED}),
    ProjectStatus.PLANNED: frozenset({ProjectStatus.GENERATING}),
    ProjectStatus.GENERATING: frozenset(
        {ProjectStatus.COMPOSED, ProjectStatus.FAILED, ProjectStatus.CANCELLED}
    ),
    ProjectStatus.COMPOSED: frozenset({ProjectStatus.AUDITING}),
    ProjectStatus.AUDITING: frozenset(
        {
            ProjectStatus.NEEDS_REPAIR,
            ProjectStatus.READY,
            ProjectStatus.FAILED,
            ProjectStatus.CANCELLED,
        }
    ),
    ProjectStatus.NEEDS_REPAIR: frozenset({ProjectStatus.GENERATING}),
    ProjectStatus.READY: frozenset({ProjectStatus.EXPORTED}),
    ProjectStatus.EXPORTED: frozenset(),
    ProjectStatus.FAILED: frozenset({ProjectStatus.GENERATING, ProjectStatus.AUDITING}),
    ProjectStatus.CANCELLED: frozenset({ProjectStatus.GENERATING, ProjectStatus.AUDITING}),
}


class InvalidTransition(Exception):
    def __init__(self, current: ProjectStatus, target: ProjectStatus) -> None:
        super().__init__(f"cannot transition from {current} to {target}")
        self.current = current
        self.target = target


def assert_transition(current: ProjectStatus, target: ProjectStatus) -> None:
    if target not in TRANSITIONS[current]:
        raise InvalidTransition(current, target)
