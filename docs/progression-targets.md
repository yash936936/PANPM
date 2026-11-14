# Progression target construction rules

This document defines source-independent safeguards for building longitudinal motor targets. It does not freeze the PPMI target windows or medication-state choice.

## Current source evidence

The PPMI source catalog identifies `NP3TOT` in `NUPDRS3TRT`, with assessment-state, form-name, medication timing and DBS fields. `LEDDLOG` contains medication and dose records with start/stop dates. Actual exports must be audited before mapping these fields.

## Selection contract

`src/data/progression_targets.py` provides two pure helpers:

- `select_motor_assessment` accepts a normalized list of motor assessments, a target date, a caller-supplied tolerance in days and an exact normalized medication-state label.
- `motor_score_change` computes follow-up minus baseline only when both records match the requested state, both scores are finite, and follow-up occurs after baseline.

Selection uses an inclusive date window and chooses the eligible assessment with the smallest absolute distance from the target date. If two eligible records are equally close, it raises `AmbiguousAssessmentError`. It does not break ties by row order or participant/record identifier. Records in other states and records with missing/non-finite scores are not eligible.

## Decisions intentionally left open

The implementation does **not** choose:

- the 12- or 24-month target date calculation;
- the permitted early/late follow-up window;
- OFF, ON or untreated as the primary medication state;
- whether to exclude DBS participants or analyze them separately;
- how to derive time-varying LEDD from medication start/stop records;
- whether baseline should use the same state rule or a separately specified baseline protocol.

Those decisions require the approved export, state-specific follow-up coverage and a prespecified protocol amendment. The 24-month primary and 12-month secondary horizon in `docs/research-protocol.md` remains unchanged.

## Leakage and reproducibility

- Resolve source state codes into normalized labels using a versioned mapping before calling the helper.
- Select baseline and follow-up assessments without examining their score values.
- Keep all records from one participant in one split.
- Record the target date, tolerance, required state, selected assessment reference and target-definition version in the restricted lineage artifact.
- Never expose future scores or progression labels to RL observations.
- Report missing targets and ambiguous selections rather than silently dropping or choosing records.

## Verification boundary

Synthetic unit tests cover state matching, inclusive window boundaries, missing scores, tied assessments, chronological ordering and score-difference direction. They do not validate PPMI source mappings, clinical appropriateness of a state rule, medication exposure, DBS handling or endpoint availability.
