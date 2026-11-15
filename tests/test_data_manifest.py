"""Tests for privacy-preserving participant coverage manifests."""
from src.data.manifest import (
    build_coverage_manifest,
    pseudonymize,
)

import pytest


SECRET = b"test-only-secret-material-at-least-32-bytes"


def test_pseudonym_is_stable_and_keyed():
    assert pseudonymize("001", SECRET) == pseudonymize("001", SECRET)
    assert pseudonymize("001", SECRET) != pseudonymize("001", b"another-test-secret-material-32bytes")


def test_short_secret_and_empty_id_are_rejected():
    with pytest.raises(ValueError, match="32 bytes"):
        pseudonymize("001", b"short")
    with pytest.raises(ValueError, match="non-empty"):
        pseudonymize("", SECRET)


def test_manifest_aggregates_series_and_never_exposes_source_id():
    rows = [
        {"participant": "001", "modality": "T1"},
        {"participant": "001", "modality": "T1"},
        {"participant": "001", "modality": "DTI"},
        {"participant": "002", "modality": "T1"},
    ]
    manifest = build_coverage_manifest(
        rows, participant_field="participant", modality_field="modality", secret=SECRET
    )
    assert len(manifest) == 2
    first = next(item for item in manifest if item["participant_key"] == pseudonymize("001", SECRET))
    assert first["has_T1"] is True
    assert first["T1_series_count"] == 2
    assert first["DTI_series_count"] == 1
    assert all("participant" not in item and "source_id" not in item for item in manifest)


def test_manifest_skips_missing_participant_or_modality():
    rows = [
        {"participant": None, "modality": "T1"},
        {"participant": "001", "modality": None},
        {"participant": "002", "modality": "T1"},
    ]
    manifest = build_coverage_manifest(
        rows, participant_field="participant", modality_field="modality", secret=SECRET
    )
    assert len(manifest) == 1
    assert manifest[0]["participant_key"] == pseudonymize("002", SECRET)
