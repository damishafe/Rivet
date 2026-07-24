import itertools

import pytest

from rivet.domain.states import TRANSITIONS, InvalidTransition, ProjectStatus, assert_transition


def test_happy_path_reaches_exported() -> None:
    order = [
        ProjectStatus.DRAFT,
        ProjectStatus.BRAND_READY,
        ProjectStatus.PLANNED,
        ProjectStatus.GENERATING,
        ProjectStatus.COMPOSED,
        ProjectStatus.AUDITING,
        ProjectStatus.READY,
        ProjectStatus.EXPORTED,
    ]
    for current, target in itertools.pairwise(order):
        assert_transition(current, target)


def test_repair_loops_back_to_generating() -> None:
    assert_transition(ProjectStatus.AUDITING, ProjectStatus.NEEDS_REPAIR)
    assert_transition(ProjectStatus.NEEDS_REPAIR, ProjectStatus.GENERATING)


def test_draft_cannot_jump_to_generating() -> None:
    with pytest.raises(InvalidTransition) as exc:
        assert_transition(ProjectStatus.DRAFT, ProjectStatus.GENERATING)
    assert exc.value.current is ProjectStatus.DRAFT


def test_every_status_has_transition_entry() -> None:
    assert set(TRANSITIONS) == set(ProjectStatus)


def test_running_states_may_fail_or_cancel() -> None:
    for running in (ProjectStatus.GENERATING, ProjectStatus.AUDITING):
        assert ProjectStatus.FAILED in TRANSITIONS[running]
        assert ProjectStatus.CANCELLED in TRANSITIONS[running]


def test_failed_resumes_only_to_running_states() -> None:
    assert TRANSITIONS[ProjectStatus.FAILED] == frozenset(
        {ProjectStatus.GENERATING, ProjectStatus.AUDITING}
    )
