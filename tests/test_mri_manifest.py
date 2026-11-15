"""Synthetic tests for local-only DICOM header indexing."""

import pytest

from src.preprocessing.mri_manifest import aggregate_header_rows


SECRET = b"panpm-mri-synthetic-test-secret-32-bytes"


def header(**overrides):
    row = {
        "PatientID": "SYNTHETIC-PARTICIPANT-001",
        "StudyInstanceUID": "1.2.840.synthetic.study.1",
        "SeriesInstanceUID": "1.2.840.synthetic.series.1",
        "SOPInstanceUID": "1.2.840.synthetic.instance.1",
        "Modality": "MR",
        "SeriesDescription": "MPRAGE",
        "ProtocolName": "Research protocol",
        "SequenceName": "tfl3d",
        "ImageType": ["ORIGINAL", "PRIMARY"],
        "MRAcquisitionType": "3D",
        "Manufacturer": "Synthetic Scanner",
        "ManufacturerModelName": "Model X",
        "MagneticFieldStrength": "3",
        "StudyDate": "20200101",
        "Rows": "256",
        "Columns": "256",
        "PixelSpacing": ["1.0", "1.0"],
        "SliceThickness": "1.0",
    }
    row.update(overrides)
    return row


def test_aggregates_instances_and_never_emits_raw_identifiers():
    result = aggregate_header_rows(
        [header(), header(SOPInstanceUID="1.2.840.synthetic.instance.2")],
        secret=SECRET,
    )
    assert result["series_count"] == 1
    series = result["series"][0]
    assert series["instance_count"] == 2
    assert series["is_mr"] is True
    assert series["is_3d"] is True
    assert series["is_original"] is True
    assert series["sequence_family"] is None
    assert series["selection_status"] == "needs_sequence_review"
    assert "SYNTHETIC-PARTICIPANT-001" not in str(result)
    assert "1.2.840.synthetic.series.1" not in str(result)


def test_does_not_infer_t1_from_series_description():
    result = aggregate_header_rows([header(SeriesDescription="T1 MPRAGE")], secret=SECRET)
    series = result["series"][0]
    assert series["sequence_family"] is None
    assert series["selection_status"] == "needs_sequence_review"


def test_marks_ambiguous_or_non_3d_headers_for_review():
    result = aggregate_header_rows(
        [header(MRAcquisitionType="2D", ImageType=["DERIVED", "SECONDARY"])],
        secret=SECRET,
    )
    series = result["series"][0]
    assert series["is_3d"] is False
    assert series["is_original"] is False
    assert series["qc_status"] == "header_review_required"
    assert "acquisition_not_unambiguously_3d" in series["qc_reasons"]


def test_detects_intra_series_metadata_conflicts():
    result = aggregate_header_rows(
        [header(), header(SOPInstanceUID="1.2.840.synthetic.instance.2", Rows="128")],
        secret=SECRET,
    )
    series = result["series"][0]
    assert series["qc_status"] == "header_review_required"
    assert "Rows" in series["header_conflicts"]


def test_skips_rows_missing_required_identifiers_without_leaking_them():
    result = aggregate_header_rows(
        [header(), header(PatientID="", SeriesInstanceUID="")],
        secret=SECRET,
    )
    assert result["counts"]["missing_patient_id"] == 1
    assert result["series_count"] == 1


def test_rejects_short_hmac_secret():
    with pytest.raises(ValueError, match="32 bytes"):
        aggregate_header_rows([header()], secret=b"too-short")
