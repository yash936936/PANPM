"""Aggregate CSV key-grain and relationship audits without exposing identifiers.

Only aggregate counts and the field names supplied by the caller are returned.
Composite key values are hashed before temporary SQLite storage. The database
exists only in memory and is discarded when each audit finishes.
"""
from __future__ import annotations

import csv
import hashlib
import hmac
import json
import secrets
import sqlite3
from collections.abc import Iterable, Sequence
from pathlib import Path

from src.data.inventory import read_csv_header


def _validate_key_fields(
    key_fields: Sequence[str], available_columns: set[str], label: str
) -> tuple[str, ...]:
    fields = tuple(key_fields)
    if not fields or any(not field for field in fields):
        raise ValueError(f"{label} must contain at least one non-empty field")
    if len(fields) != len(set(fields)):
        raise ValueError(f"{label} contains duplicate field names")
    missing = sorted(set(fields) - available_columns)
    if missing:
        raise ValueError(f"{label} fields are absent from CSV header: {missing}")
    return fields


def _key_digest(values: Sequence[str], secret: bytes) -> str:
    """Create an ephemeral keyed digest of a normalized composite key."""
    payload = json.dumps(list(values), ensure_ascii=False, separators=(",", ":"))
    return hmac.new(secret, payload.encode(), hashlib.sha256).hexdigest()


def _complete_key(row: dict[str, str], fields: Sequence[str]) -> tuple[str, ...] | None:
    values = tuple((row.get(field) or "").strip() for field in fields)
    if any(value == "" for value in values):
        return None
    return values


def _new_counter_table(connection: sqlite3.Connection, table: str) -> None:
    connection.execute(
        f"CREATE TABLE {table} (digest TEXT PRIMARY KEY, n INTEGER NOT NULL)"
    )


def _add_count(connection: sqlite3.Connection, table: str, digest: str) -> None:
    connection.execute(
        f"""
        INSERT INTO {table} (digest, n) VALUES (?, 1)
        ON CONFLICT(digest) DO UPDATE SET n = n + 1
        """,
        (digest,),
    )


def _duplicate_summary(connection: sqlite3.Connection, table: str) -> tuple[int, int, int]:
    duplicate_groups, duplicate_rows, distinct_keys = connection.execute(
        f"""
        SELECT
            COALESCE(SUM(CASE WHEN n > 1 THEN 1 ELSE 0 END), 0),
            COALESCE(SUM(CASE WHEN n > 1 THEN n - 1 ELSE 0 END), 0),
            COUNT(*)
        FROM {table}
        """
    ).fetchone()
    return int(duplicate_groups), int(duplicate_rows), int(distinct_keys)


def audit_csv_keys(
    path: str | Path,
    *,
    candidate_keys: Iterable[Sequence[str]],
) -> dict[str, object]:
    """Measure completeness and uniqueness for caller-specified candidate keys.

    This function does not assert that any candidate key is the true table
    grain. It reports the evidence so the researcher can decide after review.
    """
    candidates = [tuple(key) for key in candidate_keys]
    if not candidates:
        raise ValueError("At least one candidate key must be supplied")
    if len(candidates) != len(set(candidates)):
        raise ValueError("Candidate keys must be unique")

    columns = read_csv_header(path)
    column_set = set(columns)
    validated = [
        _validate_key_fields(key, column_set, "candidate key") for key in candidates
    ]
    counters = sqlite3.connect(":memory:")
    digest_secret = secrets.token_bytes(32)
    try:
        for index in range(len(validated)):
            _new_counter_table(counters, f"key_{index}")

        row_count = 0
        missing_counts = [0] * len(validated)
        with Path(path).open("r", encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            reader.fieldnames = [name.strip() for name in (reader.fieldnames or [])]
            for row in reader:
                row_count += 1
                for index, fields in enumerate(validated):
                    values = _complete_key(row, fields)
                    if values is None:
                        missing_counts[index] += 1
                    else:
                        _add_count(counters, f"key_{index}", _key_digest(values, digest_secret))

        results = []
        for index, fields in enumerate(validated):
            duplicate_groups, duplicate_rows, distinct_keys = _duplicate_summary(
                counters, f"key_{index}"
            )
            results.append(
                {
                    "fields": list(fields),
                    "rows_with_complete_key": row_count - missing_counts[index],
                    "rows_with_missing_key": missing_counts[index],
                    "distinct_keys": distinct_keys,
                    "duplicate_key_groups": duplicate_groups,
                    "duplicate_rows": duplicate_rows,
                }
            )
        return {"row_count": row_count, "candidate_keys": results}
    finally:
        counters.close()


def audit_csv_relationship(
    parent_path: str | Path,
    child_path: str | Path,
    *,
    parent_key: Sequence[str],
    child_key: Sequence[str],
) -> dict[str, object]:
    """Audit child-to-parent key coverage and parent-key uniqueness.

    The result reports counts only. It never returns participant IDs, image
    identifiers, or unmatched key values. Key arity must match exactly.
    """
    if len(parent_key) != len(child_key):
        raise ValueError("Parent and child keys must have the same number of fields")

    parent_columns = set(read_csv_header(parent_path))
    child_columns = set(read_csv_header(child_path))
    parent_fields = _validate_key_fields(parent_key, parent_columns, "parent key")
    child_fields = _validate_key_fields(child_key, child_columns, "child key")

    connection = sqlite3.connect(":memory:")
    digest_secret = secrets.token_bytes(32)
    try:
        _new_counter_table(connection, "parent_keys")
        parent_rows = 0
        parent_missing = 0
        with Path(parent_path).open("r", encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            reader.fieldnames = [name.strip() for name in (reader.fieldnames or [])]
            for row in reader:
                parent_rows += 1
                values = _complete_key(row, parent_fields)
                if values is None:
                    parent_missing += 1
                else:
                    _add_count(connection, "parent_keys", _key_digest(values, digest_secret))

        duplicate_groups, duplicate_rows, distinct_parent_keys = _duplicate_summary(
            connection, "parent_keys"
        )

        child_rows = 0
        child_missing = 0
        matched_rows = 0
        unmatched_rows = 0
        with Path(child_path).open("r", encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            reader.fieldnames = [name.strip() for name in (reader.fieldnames or [])]
            for row in reader:
                child_rows += 1
                values = _complete_key(row, child_fields)
                if values is None:
                    child_missing += 1
                    continue
                found = connection.execute(
                    "SELECT 1 FROM parent_keys WHERE digest = ?",
                    (_key_digest(values, digest_secret),),
                ).fetchone()
                if found:
                    matched_rows += 1
                else:
                    unmatched_rows += 1

        return {
            "parent_rows": parent_rows,
            "parent_rows_with_missing_key": parent_missing,
            "parent_distinct_keys": distinct_parent_keys,
            "parent_duplicate_key_groups": duplicate_groups,
            "parent_duplicate_rows": duplicate_rows,
            "child_rows": child_rows,
            "child_rows_with_missing_key": child_missing,
            "child_rows_matched": matched_rows,
            "child_rows_unmatched": unmatched_rows,
            "relationship_is_many_to_one_candidate": duplicate_groups == 0
            and parent_missing == 0,
        }
    finally:
        connection.close()
