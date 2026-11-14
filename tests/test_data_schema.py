"""Tests for PANPM's canonical, source-independent table contracts."""
import pytest

from src.data.schema import validate_participant_links, validate_table


def test_header_contract_accepts_minimum_columns():
    assert validate_table(
        "imaging_scans", ["scan_id", "participant_id", "modality"]
    ) == []


def test_header_contract_reports_missing_columns():
    issues = validate_table("clinical_visits", ["participant_id", "event_id"])
    assert len(issues) == 1
    assert issues[0].code == "missing_required_columns"
    assert "visit_date" in issues[0].message


def test_unknown_table_contract_is_rejected():
    with pytest.raises(ValueError, match="Unknown PANPM table"):
        validate_table("ppmi_export", ["PATNO"])


def test_unique_scan_ids_are_enforced():
    rows = [
        {"scan_id": "scan-a", "participant_id": "p1", "modality": "MRI"},
        {"scan_id": "scan-a", "participant_id": "p2", "modality": "MRI"},
    ]
    issues = validate_table(
        "imaging_scans", ["scan_id", "participant_id", "modality"], rows
    )
    assert [issue.code for issue in issues] == ["duplicate_unique_key"]


def test_null_participant_key_is_reported():
    rows = [{"participant_id": None}]
    issues = validate_table("participants", ["participant_id"], rows)
    assert issues[0].code == "null_unique_key"


def test_participant_links_detect_orphans_without_source_ids():
    participants = [{"participant_id": "p1"}]
    visits = [
        {"participant_id": "p1"},
        {"participant_id": "p2"},
        {"participant_id": None},
    ]
    issues = validate_participant_links(
        participants, clinical_visits=visits
    )
    assert [issue.row_index for issue in issues] == [1, 2]
    assert all(issue.code == "orphan_participant" for issue in issues)


def test_split_manifest_allows_same_participant_in_different_versions():
    rows = [
        {"participant_id": "p1", "split": "train", "split_version": "v1"},
        {"participant_id": "p1", "split": "test", "split_version": "v2"},
    ]
    assert validate_table(
        "split_manifest",
        ["participant_id", "split", "split_version"],
        rows,
    ) == []


def test_split_manifest_rejects_duplicate_participant_within_version():
    rows = [
        {"participant_id": "p1", "split": "train", "split_version": "v1"},
        {"participant_id": "p1", "split": "test", "split_version": "v1"},
    ]
    issues = validate_table(
        "split_manifest",
        ["participant_id", "split", "split_version"],
        rows,
    )
    assert issues[0].code == "duplicate_unique_key"


def test_duplicate_key_issue_does_not_echo_identifier_values():
    rows = [
        {"scan_id": "restricted-source-id", "participant_id": "p1", "modality": "MRI"},
        {"scan_id": "restricted-source-id", "participant_id": "p2", "modality": "MRI"},
    ]
    issues = validate_table(
        "imaging_scans", ["scan_id", "participant_id", "modality"], rows
    )
    assert issues[0].code == "duplicate_unique_key"
    assert "restricted-source-id" not in issues[0].message
