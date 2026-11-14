"""Medication-state-aware selection helpers for longitudinal motor outcomes.

These helpers operate on already normalized assessment records. They do not
map PPMI source codes, define target windows, or infer medication state.
Callers must supply a prespecified target date, tolerance, and state label.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from math import isfinite
from typing import Iterable


@dataclass(frozen=True)
class MotorAssessment:
    """One normalized motor assessment in a verified medication state."""

    assessment_id: str
    assessment_date: date
    score: float | None
    medication_state: str | None


class AmbiguousAssessmentError(ValueError):
    """Raised when equally close eligible assessments exist."""


def select_motor_assessment(
    assessments: Iterable[MotorAssessment],
    *,
    target_date: date,
    tolerance_days: int,
    required_state: str,
) -> MotorAssessment | None:
    """Select the closest valid score within an explicit window and state.

    The window is inclusive. Exact state matching is intentional: ON, OFF,
    untreated, and unknown assessments are never silently pooled. If two
    eligible assessments are equally close to the target date, the function
    raises instead of choosing one by row order or identifier.
    """
    if tolerance_days < 0:
        raise ValueError("tolerance_days must be non-negative")
    if not required_state:
        raise ValueError("required_state must be a non-empty normalized label")

    eligible: list[tuple[int, MotorAssessment]] = []
    for assessment in assessments:
        if assessment.medication_state != required_state:
            continue
        if assessment.score is None or not isfinite(assessment.score):
            continue
        distance = abs((assessment.assessment_date - target_date).days)
        if distance <= tolerance_days:
            eligible.append((distance, assessment))

    if not eligible:
        return None

    best_distance = min(distance for distance, _ in eligible)
    closest = [
        assessment for distance, assessment in eligible
        if distance == best_distance
    ]
    if len(closest) != 1:
        raise AmbiguousAssessmentError(
            "Multiple eligible motor assessments are equally close to the target date"
        )
    return closest[0]


def motor_score_change(
    baseline: MotorAssessment,
    followup: MotorAssessment,
    *,
    required_state: str,
) -> float:
    """Return follow-up minus baseline score after enforcing state consistency."""
    if baseline.medication_state != required_state:
        raise ValueError("baseline assessment does not match required_state")
    if followup.medication_state != required_state:
        raise ValueError("follow-up assessment does not match required_state")
    if baseline.score is None or not isfinite(baseline.score):
        raise ValueError("baseline score must be finite and present")
    if followup.score is None or not isfinite(followup.score):
        raise ValueError("follow-up score must be finite and present")
    if followup.assessment_date <= baseline.assessment_date:
        raise ValueError("follow-up assessment must occur after baseline")
    return float(followup.score - baseline.score)
