"""Synthetic tests for medication-state-aware motor target selection."""
from datetime import date

import pytest

from src.data.progression_targets import (
    AmbiguousAssessmentError,
    MotorAssessment,
    motor_score_change,
    select_motor_assessment,
)


def assessment(
    assessment_id: str,
    day: int,
    score: float | None,
    state: str | None = "OFF",
) -> MotorAssessment:
    return MotorAssessment(
        assessment_id=assessment_id,
        assessment_date=date(2025, 1, day),
        score=score,
        medication_state=state,
    )


def test_selects_closest_assessment_with_exact_state():
    records = [
        assessment("far-off", 20, 30.0),
        assessment("near-on", 15, 10.0, "ON"),
        assessment("near-off", 14, 25.0),
    ]

    selected = select_motor_assessment(
        records,
        target_date=date(2025, 1, 15),
        tolerance_days=5,
        required_state="OFF",
    )

    assert selected is not None
    assert selected.assessment_id == "near-off"


def test_window_boundary_is_inclusive():
    selected = select_motor_assessment(
        [assessment("boundary", 20, 20.0)],
        target_date=date(2025, 1, 15),
        tolerance_days=5,
        required_state="OFF",
    )

    assert selected is not None
    assert selected.assessment_id == "boundary"


def test_returns_none_when_no_valid_same_state_assessment_exists():
    records = [
        assessment("wrong-state", 15, 20.0, "ON"),
        assessment("missing-score", 15, None, "OFF"),
    ]

    assert select_motor_assessment(
        records,
        target_date=date(2025, 1, 15),
        tolerance_days=30,
        required_state="OFF",
    ) is None


def test_rejects_tied_closest_assessments_instead_of_arbitrary_choice():
    records = [
        assessment("before", 14, 20.0),
        assessment("after", 16, 22.0),
    ]

    with pytest.raises(AmbiguousAssessmentError):
        select_motor_assessment(
            records,
            target_date=date(2025, 1, 15),
            tolerance_days=5,
            required_state="OFF",
        )


def test_rejects_negative_tolerance_and_empty_state():
    with pytest.raises(ValueError, match="non-negative"):
        select_motor_assessment(
            [],
            target_date=date(2025, 1, 15),
            tolerance_days=-1,
            required_state="OFF",
        )
    with pytest.raises(ValueError, match="non-empty"):
        select_motor_assessment(
            [],
            target_date=date(2025, 1, 15),
            tolerance_days=30,
            required_state="",
        )


def test_change_is_followup_minus_baseline_for_same_state():
    baseline = assessment("baseline", 1, 28.0)
    followup = assessment("followup", 20, 34.0)

    assert motor_score_change(
        baseline, followup, required_state="OFF"
    ) == 6.0


def test_change_rejects_mixed_states_and_non_chronological_records():
    baseline = assessment("baseline", 1, 28.0)
    on_followup = assessment("on", 20, 25.0, "ON")
    earlier_followup = assessment("earlier", 1, 30.0)

    with pytest.raises(ValueError, match="required_state"):
        motor_score_change(baseline, on_followup, required_state="OFF")
    with pytest.raises(ValueError, match="after baseline"):
        motor_score_change(baseline, earlier_followup, required_state="OFF")
