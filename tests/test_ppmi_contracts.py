"""Tests for conservative PPMI source contracts."""
import pytest

from src.data.ppmi_contracts import (
    PPMI_SOURCE_TABLES,
    validate_ppmi_source_header,
)


def test_mri_acquisition_linkage_fields_match_annotated_dictionary():
    assert PPMI_SOURCE_TABLES["MRI_ACQUISITION"].linkage_fields == (
        "PATNO",
        "EVENT_ID",
    )


def test_mri_header_reports_missing_visit_link():
    assert validate_ppmi_source_header("MRI", ["PATNO"]) == ["EVENT_ID"]


def test_mri_acquisition_header_accepts_documented_linkage_fields():
    assert validate_ppmi_source_header(
        "MRI_ACQUISITION", ["PATNO", "EVENT_ID", "MRI_SCAN_DATE"]
    ) == []


def test_mriqc_does_not_assume_undocumented_required_keys():
    assert validate_ppmi_source_header("MRIQC", ["PATNO", "EVENT_ID"]) == []


def test_unknown_source_table_is_rejected():
    with pytest.raises(ValueError, match="Unknown documented PPMI source table"):
        validate_ppmi_source_header("NOT_A_PPMI_TABLE", ["PATNO"])
