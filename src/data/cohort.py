"""Build explicit diagnosis cohorts and leakage-safe participant splits.

This module operates on caller-supplied metadata rows only. It never reads MRI
voxels, infers source group codes, or writes participant-level manifests.
"""
from __future__ import annotations

import hashlib
from collections import Counter
from collections.abc import Mapping, Sequence
from typing import Any


DEFAULT_GROUP_MAP = {
    "HC": "HC",
    "Control": "HC",
    "PD-NC": "PD",
    "PD-MCI": "PD",
}


def build_diagnosis_cohort(
    participants: Sequence[Mapping[str, Any]],
    scans: Sequence[Mapping[str, Any]],
    *,
    group_map: Mapping[str, str] = DEFAULT_GROUP_MAP,
    include_groups: Sequence[str] = ("HC", "PD"),
    modality: str = "T1w",
) -> dict[str, Any]:
    """Create one-scan-per-participant diagnosis cohort with source labels kept.

    Each participant must have exactly one scan of the requested modality.
    Multiple scans are treated as an unresolved visit/selection decision, not
    resolved by filename sorting. The caller must supply metadata-verified
    scan rows and retain the returned participant-level records privately.
    """
    if not participants:
        raise ValueError("Participant table is empty")
    if not scans:
        raise ValueError("Scan manifest is empty")
    if not group_map or not include_groups:
        raise ValueError("Explicit group mapping and included groups are required")

    participant_by_id: dict[str, Mapping[str, Any]] = {}
    for row in participants:
        participant_id = str(row.get("participant_id", "")).strip()
        if not participant_id:
            raise ValueError("Participant row has an empty participant_id")
        if participant_id in participant_by_id:
            raise ValueError("Participant table contains duplicate participant IDs")
        participant_by_id[participant_id] = row

    scans_by_participant: dict[str, list[Mapping[str, Any]]] = {}
    unknown_scan_participants = 0
    for scan in scans:
        participant_id = str(scan.get("participant_id", "")).strip()
        if participant_id not in participant_by_id:
            unknown_scan_participants += 1
            continue
        if str(scan.get("modality", "")).strip() != modality:
            continue
        scans_by_participant.setdefault(participant_id, []).append(scan)

    records: list[dict[str, Any]] = []
    excluded: Counter[str] = Counter()
    for participant_id, participant in sorted(participant_by_id.items()):
        source_group = str(participant.get("group", "")).strip()
        normalized_group = group_map.get(source_group)
        if normalized_group is None:
            excluded["unmapped_source_group"] += 1
            continue
        if normalized_group not in include_groups:
            excluded["group_not_included"] += 1
            continue
        participant_scans = scans_by_participant.get(participant_id, [])
        if not participant_scans:
            excluded["missing_requested_modality"] += 1
            continue
        if len(participant_scans) != 1:
            excluded["ambiguous_multiple_scans"] += 1
            continue
        scan = participant_scans[0]
        scan_id = str(scan.get("scan_id", "")).strip()
        scan_path = str(scan.get("path", "")).strip()
        if not scan_id or not scan_path:
            excluded["missing_scan_identity_or_path"] += 1
            continue
        if scan.get("sequence_verified") is not True:
            excluded["sequence_not_verified"] += 1
            continue
        records.append({
            "participant_id": participant_id,
            "source_group": source_group,
            "diagnosis_label": normalized_group,
            "scan_id": scan_id,
            "scan_path": scan_path,
            "visit_id": scan.get("visit_id"),
        })

    counts = Counter(row["diagnosis_label"] for row in records)
    source_counts = Counter(row["source_group"] for row in records)
    return {
        "cohort": records,
        "included_participants": len(records),
        "diagnosis_counts": dict(sorted(counts.items())),
        "source_group_counts": dict(sorted(source_counts.items())),
        "excluded_counts_by_reason": dict(sorted(excluded.items())),
        "unknown_scan_participant_count": unknown_scan_participants,
        "modality": modality,
        "participant_level": True,
        "sequence_verification_required": True,
    }


def make_stratified_split(
    cohort: Sequence[Mapping[str, Any]],
    *,
    fractions: Mapping[str, float],
    seed: int,
    split_version: str,
    stratify_field: str = "diagnosis_label",
) -> dict[str, Any]:
    """Assign participants once to deterministic stratified train/val/test splits.

    Fractions and split names are explicit inputs. The function does not
    prescribe a train/validation/test ratio. All participants with the same ID
    are treated as one unit, and duplicate IDs are rejected.
    """
    required_splits = {"train", "validation", "test"}
    if set(fractions) != required_splits:
        raise ValueError("fractions must define train, validation and test")
    if any(not isinstance(value, (int, float)) or value < 0 for value in fractions.values()):
        raise ValueError("Split fractions must be non-negative numbers")
    if abs(sum(fractions.values()) - 1.0) > 1e-8:
        raise ValueError("Split fractions must sum to 1")
    if not split_version.strip():
        raise ValueError("split_version must be non-empty")
    if not cohort:
        raise ValueError("Cohort is empty")

    by_stratum: dict[str, list[Mapping[str, Any]]] = {}
    seen_ids: set[str] = set()
    for row in cohort:
        participant_id = str(row.get("participant_id", "")).strip()
        stratum = str(row.get(stratify_field, "")).strip()
        if not participant_id or not stratum:
            raise ValueError("Every cohort row requires participant_id and stratum")
        if participant_id in seen_ids:
            raise ValueError("Cohort contains duplicate participant IDs")
        seen_ids.add(participant_id)
        by_stratum.setdefault(stratum, []).append(row)

    split_rows: list[dict[str, Any]] = []
    for stratum in sorted(by_stratum):
        members = sorted(
            by_stratum[stratum],
            key=lambda row: hashlib.sha256(
                f"{seed}:{row['participant_id']}".encode("utf-8")
            ).digest(),
        )
        exact = {name: len(members) * fractions[name] for name in required_splits}
        allocations = {name: int(exact[name]) for name in required_splits}
        remainder = len(members) - sum(allocations.values())
        order = sorted(required_splits, key=lambda name: (exact[name] - allocations[name], name), reverse=True)
        for name in order[:remainder]:
            allocations[name] += 1
        cursor = 0
        for name in ("train", "validation", "test"):
            for member in members[cursor : cursor + allocations[name]]:
                split_rows.append({
                    "participant_id": str(member["participant_id"]),
                    "stratum": stratum,
                    "split": name,
                    "split_version": split_version,
                })
            cursor += allocations[name]

    split_counts = Counter(row["split"] for row in split_rows)
    stratum_counts: dict[str, dict[str, int]] = {}
    for row in split_rows:
        stratum_counts.setdefault(row["stratum"], Counter())[row["split"]] += 1
    return {
        "assignments": sorted(split_rows, key=lambda row: row["participant_id"]),
        "participant_count": len(split_rows),
        "split_counts": {name: split_counts.get(name, 0) for name in ("train", "validation", "test")},
        "stratum_split_counts": {
            stratum: {name: counts.get(name, 0) for name in ("train", "validation", "test")}
            for stratum, counts in sorted(stratum_counts.items())
        },
        "seed": seed,
        "fractions": {name: float(fractions[name]) for name in ("train", "validation", "test")},
        "split_version": split_version,
        "stratify_field": stratify_field,
        "participant_level": True,
    }
