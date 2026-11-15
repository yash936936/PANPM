"""Validate explicit mappings from source export columns to PANPM fields.

This module deliberately does not guess PPMI column names. Mapping files are
provided by the researcher after inspecting the exact export headers.
"""
from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass


@dataclass(frozen=True)
class MappingSpec:
    """A source-to-normalized column mapping for one export."""

    source_to_target: Mapping[str, str]
    required_targets: frozenset[str]

    def validate(self, source_columns: Iterable[str]) -> None:
        """Raise ValueError when source columns or required targets are absent."""
        available = set(source_columns)
        missing_sources = sorted(set(self.source_to_target) - available)
        if missing_sources:
            raise ValueError(f"Mapped source columns are absent: {missing_sources}")

        targets = list(self.source_to_target.values())
        duplicates = sorted({name for name in targets if targets.count(name) > 1})
        if duplicates:
            raise ValueError(f"Multiple source columns map to the same target: {duplicates}")

        missing_targets = sorted(self.required_targets - set(targets))
        if missing_targets:
            raise ValueError(f"Required normalized targets are unmapped: {missing_targets}")

    def normalize_record(self, record: Mapping[str, object]) -> dict[str, object]:
        """Return only explicitly mapped fields, without altering source values."""
        self.validate(record.keys())
        return {
            target: record[source]
            for source, target in self.source_to_target.items()
        }
