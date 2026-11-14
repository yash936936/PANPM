"""Create pseudonymous participant coverage manifests from approved metadata."""
from __future__ import annotations

import hashlib
import hmac
from collections import defaultdict
from typing import Iterable, Mapping


def pseudonymize(source_id: str, secret: bytes, namespace: str = "panpm-v1") -> str:
    """Create a stable keyed pseudonym; never use an unhashed source identifier."""
    if not source_id or not source_id.strip():
        raise ValueError("source_id must be non-empty")
    if len(secret) < 32:
        raise ValueError("secret must contain at least 32 bytes")
    message = f"{namespace}:{source_id.strip()}".encode("utf-8")
    return hmac.new(secret, message, hashlib.sha256).hexdigest()


def build_coverage_manifest(
    rows: Iterable[Mapping[str, object]],
    *,
    participant_field: str,
    modality_field: str,
    secret: bytes,
) -> list[dict[str, object]]:
    """Aggregate participant-by-modality presence without exposing source IDs.

    Rows are series-level records. Repeated series for a participant/modality
    increment series_count but do not create duplicate modality-presence flags.
    """
    counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for row in rows:
        if participant_field not in row or modality_field not in row:
            raise ValueError("Configured participant/modality field is missing")
        source_id = str(row[participant_field]).strip()
        modality = str(row[modality_field]).strip()
        if not source_id or not modality:
            continue
        participant_key = pseudonymize(source_id, secret)
        counts[participant_key][modality] += 1

    output: list[dict[str, object]] = []
    for participant_key, modalities in sorted(counts.items()):
        item: dict[str, object] = {"participant_key": participant_key}
        for modality, series_count in sorted(modalities.items()):
            item[f"has_{modality}"] = True
            item[f"{modality}_series_count"] = series_count
        output.append(item)
    return output
