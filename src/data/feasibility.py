"""Build aggregate Phase 0 coverage reports from explicitly configured CSV exports.

All participant and image join keys are represented only by ephemeral HMAC
digests in memory. The report contains counts, configured field names and
provenance metadata, never source identifiers or file-system paths.
"""
from __future__ import annotations

import calendar
import csv
import hashlib
import hmac
import json
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from datetime import date, datetime
from pathlib import Path
from typing import Any

from src.data.source_mapping import MappingSpec


def load_mapping_config(path: str | Path) -> dict[str, Any]:
    """Load and validate a release-specific JSON mapping configuration."""
    config = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(config, dict):
        raise ValueError("Mapping configuration must be a JSON object")
    if not str(config.get("release_id", "")).strip():
        raise ValueError("Configuration requires a non-empty release_id")
    tables = config.get("tables")
    if not isinstance(tables, dict) or not tables:
        raise ValueError("Configuration requires a non-empty tables object")
    for table_name, table in tables.items():
        if not isinstance(table, dict):
            raise ValueError(f"Table configuration must be an object: {table_name}")
        mapping = table.get("source_to_target")
        required = table.get("required_targets", [])
        if not isinstance(mapping, dict) or not isinstance(required, list):
            raise ValueError(f"Invalid mapping definition for table: {table_name}")
        spec = MappingSpec(mapping, frozenset(required))
        # Validate target uniqueness and required target coverage now.
        targets = list(mapping.values())
        if any(not isinstance(source, str) or not source for source in mapping):
            raise ValueError(f"Invalid source field in table: {table_name}")
        if any(not isinstance(target, str) or not target for target in targets):
            raise ValueError(f"Invalid target field in table: {table_name}")
        if len(targets) != len(set(targets)):
            raise ValueError(f"Duplicate target fields in table: {table_name}")
        if not spec.required_targets.issubset(set(targets)):
            raise ValueError(f"Required targets are unmapped in table: {table_name}")
    return config


def validate_configured_header(
    table_name: str,
    source_columns: Sequence[str],
    config: Mapping[str, Any],
) -> None:
    """Validate a real export header against one configured table mapping."""
    try:
        table = config["tables"][table_name]
    except (KeyError, TypeError) as exc:
        raise ValueError(f"No configured mapping for table: {table_name}") from exc
    spec = MappingSpec(
        table["source_to_target"], frozenset(table.get("required_targets", []))
    )
    spec.validate(source_columns)


def normalize_configured_rows(
    table_name: str,
    rows: Sequence[Mapping[str, object]],
    config: Mapping[str, Any],
) -> list[dict[str, object]]:
    """Normalize records using only a configured source-to-target mapping."""
    try:
        table = config["tables"][table_name]
    except (KeyError, TypeError) as exc:
        raise ValueError(f"No configured mapping for table: {table_name}") from exc
    spec = MappingSpec(
        table["source_to_target"], frozenset(table.get("required_targets", []))
    )
    normalized = []
    for row in rows:
        spec.validate(row.keys())
        normalized.append(spec.normalize_record(row))
    return normalized


def _read_rows(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if not reader.fieldnames:
            raise ValueError(f"CSV has no header: {Path(path).name}")
        reader.fieldnames = [name.strip() for name in reader.fieldnames]
        return [
            {str(key).strip(): (value or "").strip() for key, value in row.items() if key}
            for row in reader
        ]


def _require_fields(rows: Sequence[Mapping[str, str]], fields: Sequence[str]) -> None:
    if not rows:
        return
    available = set(rows[0])
    missing = sorted(set(fields) - available)
    if missing:
        raise ValueError(f"Configured source fields are absent: {missing}")


def _digest(values: Sequence[str], secret: bytes) -> str:
    if len(secret) < 32:
        raise ValueError("HMAC secret must contain at least 32 bytes")
    payload = json.dumps(list(values), separators=(",", ":"), ensure_ascii=False)
    return hmac.new(secret, payload.encode(), hashlib.sha256).hexdigest()


def _date(value: str) -> date | None:
    if not value:
        return None
    for pattern in ("%Y-%m-%d", "%m/%d/%Y", "%d-%b-%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(value[:10], pattern).date()
        except ValueError:
            continue
    return None


def cohort_coverage(
    status_csv: str | Path,
    *,
    participant_field: str,
    cohort_field: str,
    enrollment_field: str | None,
    secret: bytes,
) -> dict[str, Any]:
    """Count distinct participants by raw cohort/enrollment values."""
    rows = _read_rows(status_csv)
    fields = [participant_field, cohort_field]
    if enrollment_field:
        fields.append(enrollment_field)
    _require_fields(rows, fields)
    groups: dict[tuple[str, str], set[str]] = defaultdict(set)
    for row in rows:
        participant = row.get(participant_field, "").strip()
        cohort = row.get(cohort_field, "").strip() or "MISSING"
        enrollment = row.get(enrollment_field, "").strip() if enrollment_field else "ALL"
        if participant:
            groups[(cohort, enrollment or "MISSING")].add(_digest([participant], secret))
    return {
        "source_rows": len(rows),
        "groups": [
            {
                "raw_cohort": cohort,
                "raw_enrollment_status": enrollment,
                "distinct_participants": len(participants),
            }
            for (cohort, enrollment), participants in sorted(groups.items())
        ],
    }


def mri_manifest_matching(
    acquisitions_csv: str | Path,
    image_manifest_csv: str | Path,
    *,
    acquisition_key: Sequence[str],
    manifest_key: Sequence[str],
    sequence_flags: Mapping[str, str],
    secret: bytes,
) -> dict[str, Any]:
    """Match acquisition rows to image-manifest rows using explicit join keys.

    sequence_flags maps a normalized family label to an acquisition CSV flag
    field. A flag is counted as present only for values explicitly in
    {"1", "true", "yes", "y"}; source-specific code mappings must be handled
    before calling this function.
    """
    if not acquisition_key or len(acquisition_key) != len(manifest_key):
        raise ValueError("Acquisition and manifest keys must have equal non-zero arity")
    acquisitions = _read_rows(acquisitions_csv)
    manifest = _read_rows(image_manifest_csv)
    _require_fields(acquisitions, [*acquisition_key, *sequence_flags.values()])
    _require_fields(manifest, manifest_key)

    acq_counts: Counter[str] = Counter()
    manifest_counts: Counter[str] = Counter()
    for row in acquisitions:
        values = [row.get(field, "") for field in acquisition_key]
        if all(values):
            acq_counts[_digest(values, secret)] += 1
    for row in manifest:
        values = [row.get(field, "") for field in manifest_key]
        if all(values):
            manifest_counts[_digest(values, secret)] += 1
    manifest_keys = set(manifest_counts)

    matched = sum(count for key, count in acq_counts.items() if key in manifest_keys)
    unmatched = sum(count for key, count in acq_counts.items() if key not in manifest_keys)
    manifest_matched = sum(1 for key in manifest_keys if key in acq_counts)
    manifest_unmatched = len(manifest_keys) - manifest_matched
    sequence_coverage = []
    for family, flag in sorted(sequence_flags.items()):
        selected = [
            row for row in acquisitions
            if row.get(flag, "").strip().lower() in {"1", "true", "yes", "y"}
        ]
        selected_matched = sum(
            1 for row in selected
            if all(row.get(field, "") for field in acquisition_key)
            and _digest([row[field] for field in acquisition_key], secret) in manifest_keys
        )
        sequence_coverage.append({
            "sequence_family": family,
            "acquisition_rows_flagged": len(selected),
            "flagged_rows_matched_to_manifest": selected_matched,
        })
    return {
        "acquisition_rows": len(acquisitions),
        "acquisition_rows_with_complete_key": sum(acq_counts.values()),
        "acquisition_rows_missing_join_key": len(acquisitions) - sum(acq_counts.values()),
        "acquisition_duplicate_key_groups": sum(1 for n in acq_counts.values() if n > 1),
        "image_manifest_rows": len(manifest),
        "manifest_rows_with_complete_key": sum(manifest_counts.values()),
        "manifest_rows_missing_join_key": len(manifest) - sum(manifest_counts.values()),
        "manifest_duplicate_key_groups": sum(1 for n in manifest_counts.values() if n > 1),
        "manifest_duplicate_rows": sum(n - 1 for n in manifest_counts.values() if n > 1),
        "distinct_manifest_keys": len(manifest_keys),
        "acquisition_rows_matched": matched,
        "acquisition_rows_unmatched": unmatched,
        "manifest_keys_matched": manifest_matched,
        "manifest_keys_unmatched": manifest_unmatched,
        "sequence_coverage": sequence_coverage,
        "join_key_acquisition": list(acquisition_key),
        "join_key_manifest": list(manifest_key),
    }


def progression_endpoint_coverage(
    baselines_csv: str | Path,
    assessments_csv: str | Path,
    *,
    participant_field: str,
    index_date_field: str,
    assessment_date_field: str,
    score_field: str,
    state_field: str,
    assessment_form_field: str,
    allowed_assessment_forms: Sequence[str],
    state_map: Mapping[str, str],
    target_states: Sequence[str],
    horizons_months: Sequence[int],
    tolerance_days: int,
    secret: bytes,
    ledd_csv: str | Path | None = None,
    ledd_participant_field: str | None = None,
) -> dict[str, Any]:
    """Estimate exact-state baseline/follow-up score availability by horizon.

    This is a feasibility count, not a clinical endpoint decision. The caller
    supplies source-state mapping, horizon, tolerance and target state. Ties at
    the nearest eligible date are counted as ambiguous and excluded.
    """
    if tolerance_days < 0 or any(month < 1 for month in horizons_months):
        raise ValueError("Horizon months must be positive and tolerance non-negative")
    if not state_map or not target_states:
        raise ValueError("Explicit source state_map and target_states are required")
    baselines = _read_rows(baselines_csv)
    assessments = _read_rows(assessments_csv)
    _require_fields(baselines, [participant_field, index_date_field])
    _require_fields(
        assessments,
        [participant_field, assessment_date_field, score_field, state_field, assessment_form_field],
    )

    baseline_candidates: dict[str, list[date]] = defaultdict(list)
    for row in baselines:
        pid = row.get(participant_field, "")
        index_date = _date(row.get(index_date_field, ""))
        if pid and index_date is not None:
            baseline_candidates[_digest([pid], secret)].append(index_date)
    ambiguous_baseline_keys = {
        key for key, values in baseline_candidates.items() if len(values) > 1
    }
    baseline_by_id = {
        key: values[0]
        for key, values in baseline_candidates.items()
        if len(values) == 1
    }
    baseline_ambiguous = len(ambiguous_baseline_keys)

    by_participant_state: dict[tuple[str, str], list[tuple[date, float]]] = defaultdict(list)
    unknown_states = 0
    missing_score_or_date = 0
    excluded_form_rows = 0
    allowed_forms = set(allowed_assessment_forms)
    if not allowed_forms:
        raise ValueError("At least one explicitly approved assessment form is required")
    for row in assessments:
        pid = row.get(participant_field, "")
        raw_state = row.get(state_field, "")
        normalized_state = state_map.get(raw_state)
        if row.get(assessment_form_field, "") not in allowed_forms:
            excluded_form_rows += 1
            continue
        assessment_date = _date(row.get(assessment_date_field, ""))
        try:
            score = float(row.get(score_field, ""))
        except (TypeError, ValueError):
            score = None
        if not normalized_state:
            unknown_states += 1
            continue
        if not pid or assessment_date is None or score is None:
            missing_score_or_date += 1
            continue
        digest = _digest([pid], secret)
        if digest in baseline_by_id:
            by_participant_state[(digest, normalized_state)].append((assessment_date, score))

    def closest(
        candidates: Sequence[tuple[date, float]],
        target: date,
        *,
        after: date | None = None,
    ) -> tuple[str, date | None, float | None]:
        eligible = [
            (abs((when - target).days), when, score)
            for when, score in candidates
            if abs((when - target).days) <= tolerance_days
            and (after is None or when > after)
        ]
        if not eligible:
            return "missing", None, None
        minimum = min(days for days, _, _ in eligible)
        nearest = [(when, score) for days, when, score in eligible if days == minimum]
        if len(nearest) != 1:
            return "ambiguous", None, None
        return "valid", nearest[0][0], nearest[0][1]

    results = []
    for state in target_states:
        baseline_valid = 0
        baseline_missing = 0
        baseline_ambiguous_count = 0
        per_horizon = []
        for participant_key, index_date in baseline_by_id.items():
            status, _, _ = closest(by_participant_state.get((participant_key, state), []), index_date)
            if status == "valid":
                baseline_valid += 1
            elif status == "ambiguous":
                baseline_ambiguous_count += 1
            else:
                baseline_missing += 1
        for horizon in horizons_months:
            valid = missing = ambiguous = 0
            for participant_key, index_date in baseline_by_id.items():
                candidates = by_participant_state.get((participant_key, state), [])
                base_status, baseline_assessment_date, _ = closest(candidates, index_date)
                if base_status != "valid" or baseline_assessment_date is None:
                    if base_status == "ambiguous":
                        ambiguous += 1
                    else:
                        missing += 1
                    continue
                # Use calendar-month arithmetic with day clamped to month end.
                month_index = index_date.month - 1 + horizon
                year = index_date.year + month_index // 12
                month = month_index % 12 + 1
                target_day = min(index_date.day, calendar.monthrange(year, month)[1])
                target_date = date(year, month, target_day)
                follow_status, _, _ = closest(candidates, target_date, after=baseline_assessment_date)
                if follow_status == "valid":
                    valid += 1
                elif follow_status == "ambiguous":
                    ambiguous += 1
                else:
                    missing += 1
            per_horizon.append({
                "horizon_months": horizon,
                "participants_with_valid_same_state_baseline_and_followup": valid,
                "participants_missing_or_invalid": missing,
                "participants_with_tied_nearest_assessment": ambiguous,
            })
        results.append({
            "target_state": state,
            "participants_with_valid_baseline": baseline_valid,
            "participants_missing_baseline": baseline_missing,
            "participants_with_ambiguous_baseline": baseline_ambiguous_count,
            "horizons": per_horizon,
        })

    ledd_summary = None
    if ledd_csv:
        if not ledd_participant_field:
            raise ValueError("ledd_participant_field is required when ledd_csv is supplied")
        ledd_rows = _read_rows(ledd_csv)
        _require_fields(ledd_rows, [ledd_participant_field])
        ledd_ids = {
            _digest([row[ledd_participant_field]], secret)
            for row in ledd_rows if row.get(ledd_participant_field, "")
        }
        ledd_summary = {
            "rows": len(ledd_rows),
            "participants_with_any_ledd_record": len(ledd_ids),
            "baseline_participants_with_any_ledd_record":
                len(ledd_ids.intersection(baseline_by_id)),
        }
    return {
        "baseline_participants": len(baseline_by_id),
        "duplicate_or_ambiguous_baseline_participants": baseline_ambiguous,
        "assessment_rows": len(assessments),
        "assessment_rows_with_unknown_state": unknown_states,
        "assessment_rows_excluded_by_form": excluded_form_rows,
        "assessment_rows_missing_score_or_date": missing_score_or_date,
        "state_coverage": results,
        "ledd_coverage": ledd_summary,
        "rule": {
            "date_tolerance_days": tolerance_days,
            "target_states": list(target_states),
            "allowed_assessment_forms": sorted(allowed_forms),
            "horizons_months": list(horizons_months),
            "same_state_required": True,
            "tie_policy": "exclude_as_ambiguous",
        },
    }


def build_phase0_report(
    *,
    release_id: str,
    download_date: str,
    source_checksums: Mapping[str, str],
    mapping_config_sha256: str,
    cohort: Mapping[str, Any],
    imaging: Mapping[str, Any],
    progression: Mapping[str, Any],
) -> dict[str, Any]:
    """Assemble a provenance-backed report with no participant-level records."""
    try:
        date.fromisoformat(download_date)
    except ValueError as exc:
        raise ValueError("download_date must use ISO YYYY-MM-DD format") from exc
    if not release_id.strip() or not source_checksums or len(mapping_config_sha256) != 64:
        raise ValueError("release_id, source checksums and mapping config SHA-256 are required")
    digests = [*source_checksums.values(), mapping_config_sha256]
    try:
        if any(len(value) != 64 for value in digests):
            raise ValueError
        for value in digests:
            int(value, 16)
    except (TypeError, ValueError) as exc:
        raise ValueError("Every source and config checksum must be a SHA-256 hex digest") from exc
    return {
        "report_schema_version": "1.0",
        "release_id": release_id,
        "download_date": download_date,
        "source_sha256": dict(sorted(source_checksums.items())),
        "mapping_config_sha256": mapping_config_sha256,
        "evidence_class": "metadata_feasibility_only",
        "cohort_coverage": dict(cohort),
        "mri_image_manifest_matching": dict(imaging),
        "progression_endpoint_coverage": dict(progression),
        "training_readiness": {
            "status": "not_assessed_by_phase0_report",
            "model_training_authorized_by_report": False,
            "requires_manual_review": True,
        },
    }
