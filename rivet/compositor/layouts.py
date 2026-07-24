from typing import Literal, TypeGuard

LayoutTemplate = Literal["center_hero", "split_proof", "cta_lockup"]

LAYOUTS: tuple[LayoutTemplate, ...] = ("center_hero", "split_proof", "cta_lockup")


def is_layout(value: str) -> TypeGuard[LayoutTemplate]:
    return value in LAYOUTS
