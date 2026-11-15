"""Tests for diagnosis cohort construction and participant-level split logic."""
import pytest

from src.data.cohort import build_diagnosis_cohort, make_stratified_split


def _participants():
    return [
        {"participant_id": "sub-01", "group": "HC"},
        {"participant_id": "sub-02", "group": "PD-NC"},
        {"participant_id": "sub-03", "group": "PD-MCI"},
    ]


def _scans():
    return [
        {
            "participant_id": "sub-01",
            "scan_id": "scan-01",
            "path": "/private/sub-01_T1w.nii.gz",
            "modality": "T1w",
            "sequence_verified": True,
        },
        {
            "participant_id": "sub-02",
            "scan_id": "scan-02",
            "path": "/private/sub-02_T1w.nii.gz",
            "modality": "T1w",
            "sequence_verified": True,
        },
        {
            "participant_id": "sub-03",
            "scan_id": "scan-03",
            "path": "/private/sub-03_T1w.nii.gz",
            "modality": "T1w",
            "sequence_verified": True,
        },
    ]


def test_diagnosis_cohort_preserves_source_groups_and_binary_labels():
    result = build_diagnosis_cohort(_participants(), _scans())
    assert result["included_participants"] == 3
    assert result["diagnosis_counts"] == {"HC": 1, "PD": 2}
    assert result["source_group_counts"] == {"HC": 1, "PD-MCI": 1, "PD-NC": 1}
    assert {row["source_group"] for row in result["cohort"]} == {
        "HC", "PD-NC", "PD-MCI"
    }


def test_unverified_sequence_is_not_included():
    scans = _scans()
    scans[0] = {**scans[0], "sequence_verified": False}
    result = build_diagnosis_cohort(_participants(), scans)
    assert result["included_participants"] == 2
    assert result["excluded_counts_by_reason"]["sequence_not_verified"] == 1


def test_multiple_scans_are_ambiguous_not_silently_selected():
    scans = _scans()
    scans.append({**scans[0], "scan_id": "scan-01-extra"})
    result = build_diagnosis_cohort(_participants(), scans)
    assert result["excluded_counts_by_reason"]["ambiguous_multiple_scans"] == 1


def test_duplicate_participant_rows_are_rejected():
    with pytest.raises(ValueError, match="duplicate participant"):
        build_diagnosis_cohort(_participants() + [_participants()[0]], _scans())


def test_split_is_reproducible_and_participant_disjoint():
    cohort = [
        {"participant_id": f"p{i}", "diagnosis_label": "PD" if i < 10 else "HC"}
        for i in range(20)
    ]
    kwargs = {
        "fractions": {"train": 0.6, "validation": 0.2, "test": 0.2},
        "seed": 17,
        "split_version": "pilot-v1",
    }
    first = make_stratified_split(cohort, **kwargs)
    second = make_stratified_split(cohort, **kwargs)
    assert first == second
    ids = [row["participant_id"] for row in first["assignments"]]
    assert len(ids) == len(set(ids)) == 20


def test_split_stratifies_each_label_and_uses_all_participants():
    cohort = [
        {"participant_id": f"p{i}", "diagnosis_label": "PD" if i < 10 else "HC"}
        for i in range(20)
    ]
    result = make_stratified_split(
        cohort,
        fractions={"train": 0.6, "validation": 0.2, "test": 0.2},
        seed=3,
        split_version="v1",
    )
    assert result["participant_count"] == 20
    assert result["split_counts"] == {"train": 12, "validation": 4, "test": 4}
    assert result["stratum_split_counts"]["PD"] == {
        "train": 6, "validation": 2, "test": 2
    }
    assert result["stratum_split_counts"]["HC"] == {
        "train": 6, "validation": 2, "test": 2
    }


def test_split_rejects_duplicate_ids_and_bad_fractions():
    cohort = [
        {"participant_id": "p1", "diagnosis_label": "PD"},
        {"participant_id": "p1", "diagnosis_label": "PD"},
    ]
    with pytest.raises(ValueError, match="duplicate participant"):
        make_stratified_split(
            cohort,
            fractions={"train": 0.6, "validation": 0.2, "test": 0.2},
            seed=1,
            split_version="v1",
        )
    with pytest.raises(ValueError, match="sum to 1"):
        make_stratified_split(
            [{"participant_id": "p1", "diagnosis_label": "PD"}],
            fractions={"train": 0.5, "validation": 0.2, "test": 0.2},
            seed=1,
            split_version="v1",
        )


def test_duplicate_scan_issue_does_not_echo_participant_identifier():
    rows = _participants() + [_participants()[0]]
    with pytest.raises(ValueError) as error:
        build_diagnosis_cohort(rows, _scans())
    assert "sub-01" not in str(error.value)
