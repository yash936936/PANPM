"""Canonical PANPM table contracts and relational checks.

These contracts describe PANPM's internal schema, not PPMI source headers.
Source exports must be mapped explicitly before validation. Required fields are
limited to the keys needed to identify each table's documented grain.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping, Sequence


@dataclass(frozen=True)
class TableContract:
    """Minimum required columns and optional unique key for a normalized table."""

    name: str
    required_columns: frozenset[str]
    unique_key: tuple[str, ...] = ()


CONTRACTS: dict[str, TableContract] = {
    "participants": TableContract(
        "participants", frozenset({"participant_id"}), ("participant_id",)
    ),
    "clinical_visits": TableContract(
        "clinical_visits",
        frozenset({"participant_id", "event_id", "visit_date"}),
    ),
    "imaging_scans": TableContract(
        "imaging_scans",
        frozenset({"scan_id", "participant_id", "modality"}),
        ("scan_id",),
    ),
    "progression_targets": TableContract(
        "progression_targets",
        frozenset({"participant_id", "horizon_months", "target_valid"}),
    ),
    "split_manifest": TableContract(
        "split_manifest",
        frozenset({"participant_id", "split", "split_version"}),
        ("participant_id", "split_version"),
    ),
}


@dataclass(frozen=True)
class ValidationIssue:
    """A machine-readable schema or relationship problem."""

    table: str
    code: str
    message: str
    row_index: int | None = None


def validate_table(
    table_name: str,
    columns: Iterable[str],
    rows: Sequence[Mapping[str, object]] | None = None,
) -> list[ValidationIssue]:
    """Check required columns, null keys and declared unique keys.

    Rows are optional so the same contract can validate a CSV header before
    loading data. No source field names are inferred.
    """
    if table_name not in CONTRACTS:
        raise ValueError(f"Unknown PANPM table contract: {table_name}")

    contract = CONTRACTS[table_name]
    available = set(columns)
    issues: list[ValidationIssue] = []
    missing = sorted(contract.required_columns - available)
    if missing:
        issues.append(
            ValidationIssue(
                table_name,
                "missing_required_columns",
                f"Missing required columns: {missing}",
            )
        )
        return issues

    if rows is None or not contract.unique_key:
        return issues

    seen: dict[tuple[object, ...], int] = {}
    for index, row in enumerate(rows):
        key = tuple(row.get(field) for field in contract.unique_key)
        if any(value is None or value == "" for value in key):
            issues.append(
                ValidationIssue(
                    table_name,
                    "null_unique_key",
                    f"Unique key {contract.unique_key} contains a null or empty value",
                    index,
                )
            )
            continue
        if key in seen:
            issues.append(
                ValidationIssue(
                    table_name,
                    "duplicate_unique_key",
                    f"Unique key duplicates row {seen[key]}",
                    index,
                )
            )
        else:
            seen[key] = index
    return issues


def validate_participant_links(
    participants: Sequence[Mapping[str, object]],
    **tables: Sequence[Mapping[str, object]],
) -> list[ValidationIssue]:
    """Check participant foreign keys without exposing source identifiers."""
    known_ids = {
        row.get("participant_id")
        for row in participants
        if row.get("participant_id") not in (None, "")
    }
    issues: list[ValidationIssue] = []
    for table_name, rows in tables.items():
        if table_name not in {
            "clinical_visits",
            "imaging_scans",
            "progression_targets",
            "split_manifest",
        }:
            raise ValueError(f"Unsupported participant-linked table: {table_name}")
        for index, row in enumerate(rows):
            participant_id = row.get("participant_id")
            if participant_id in (None, "") or participant_id not in known_ids:
                issues.append(
                    ValidationIssue(
                        table_name,
                        "orphan_participant",
                        "participant_id is missing or absent from participants",
                        index,
                    )
                )
    return issues
