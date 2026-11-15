"""Synthetic tests for the aggregate Phase 0 feasibility pipeline."""
import json

import pytest

from src.data.feasibility import (
    build_phase0_report,
    cohort_coverage,
    load_mapping_config,
    mri_manifest_matching,
    normalize_configured_rows,
    progression_endpoint_coverage,
)

SECRET = b"phase0-test-secret-material-minimum-32-bytes"


def test_mapping_config_and_explicit_normalization(tmp_path):
    config_path = tmp_path / "mapping.json"
    config_path.write_text(json.dumps({
        "release_id": "synthetic-r1",
        "tables": {
            "PATIENT_STATUS": {
                "source_to_target": {"PATNO": "source_participant_id", "COHORT": "cohort_code"},
                "required_targets": ["source_participant_id", "cohort_code"],
            }
        },
    }), encoding="utf-8")
    config = load_mapping_config(config_path)
    result = normalize_configured_rows(
        "PATIENT_STATUS", [{"PATNO": "001", "COHORT": "1", "UNUSED": "x"}], config
    )
    assert result == [{"source_participant_id": "001", "cohort_code": "1"}]
    with pytest.raises(ValueError, match="absent"):
        normalize_configured_rows("PATIENT_STATUS", [{"PATNO": "001"}], config)


def test_mapping_config_rejects_missing_required_target(tmp_path):
    path = tmp_path / "mapping.json"
    path.write_text(json.dumps({
        "release_id": "r1",
        "tables": {"T": {"source_to_target": {"A": "a"}, "required_targets": ["b"]}},
    }), encoding="utf-8")
    with pytest.raises(ValueError, match="Required targets"):
        load_mapping_config(path)


def test_cohort_coverage_counts_distinct_people_and_preserves_codes(tmp_path):
    path = tmp_path / "status.csv"
    path.write_text(
        "PATNO,COHORT,ENROLL_STATUS\n001,1,ENROLLED\n001,1,ENROLLED\n002,2,ENROLLED\n",
        encoding="utf-8",
    )
    result = cohort_coverage(
        path, participant_field="PATNO", cohort_field="COHORT",
        enrollment_field="ENROLL_STATUS", secret=SECRET,
    )
    assert result["source_rows"] == 3
    assert result["groups"][0]["distinct_participants"] == 1
    assert "001" not in str(result)


def test_mri_matching_reports_join_and_sequence_coverage(tmp_path):
    acq = tmp_path / "acq.csv"
    manifest = tmp_path / "manifest.csv"
    acq.write_text(
        "PATNO,EVENT_ID,T1_FLAG\n001,BL,1\n002,BL,1\n",
        encoding="utf-8",
    )
    manifest.write_text(
        "SUBJECT,VISIT\n001,BL\n",
        encoding="utf-8",
    )
    result = mri_manifest_matching(
        acq, manifest, acquisition_key=("PATNO", "EVENT_ID"),
        manifest_key=("SUBJECT", "VISIT"), sequence_flags={"T1": "T1_FLAG"},
        secret=SECRET,
    )
    assert result["acquisition_rows_matched"] == 1
    assert result["acquisition_rows_unmatched"] == 1
    assert result["sequence_coverage"][0]["flagged_rows_matched_to_manifest"] == 1


def test_progression_coverage_requires_same_state_and_excludes_ties(tmp_path):
    baseline = tmp_path / "baseline.csv"
    assessments = tmp_path / "assessments.csv"
    baseline.write_text(
        "PATNO,INDEX_DATE\n001,2020-01-01\n002,2020-01-01\n",
        encoding="utf-8",
    )
    assessments.write_text(
        "PATNO,EXAMDT,NP3TOT,PDSTATE\n"
        "001,2020-01-01,20,OFF\n"
        "001,2021-01-01,25,OFF\n"
        "002,2020-01-01,30,OFF\n"
        "002,2021-01-01,35,OFF\n"
        "002,2021-01-01,36,OFF\n"
        "001,2021-01-01,10,ON\n",
        encoding="utf-8",
    )
    result = progression_endpoint_coverage(
        baseline, assessments, participant_field="PATNO", index_date_field="INDEX_DATE",
        assessment_date_field="EXAMDT", score_field="NP3TOT", state_field="PDSTATE",
        state_map={"OFF": "OFF", "ON": "ON"}, target_states=["OFF"],
        horizons_months=[12], tolerance_days=30, secret=SECRET,
    )
    off = result["state_coverage"][0]
    assert off["participants_with_valid_baseline"] == 2
    assert off["horizons"][0]["participants_with_valid_same_state_baseline_and_followup"] == 1
    assert off["horizons"][0]["participants_with_tied_nearest_assessment"] == 1


def test_phase0_report_does_not_claim_training_readiness():
    result = build_phase0_report(
        release_id="r1", download_date="2026-11-15",
        cohort={"groups": []}, imaging={}, progression={},
    )
    assert result["training_readiness"]["participant_level_data_fetch_verified"] is False
    assert result["training_readiness"]["model_training_authorized_by_report"] is False
