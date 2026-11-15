"""Synthetic tests for first-pass BOLD temporal QC."""
import json

import nibabel as nib
import numpy as np
import pytest

from src.preprocessing.bold_qc import (
    aggregate_bold_qc,
    inspect_bold,
    render_bold_montage,
)


def _write_bold(tmp_path, *, tr=2.0, mismatch=False, metadata=None, affine=None):
    path = tmp_path / "sub-test_task-rest_bold.nii.gz"
    sidecar = tmp_path / "sub-test_task-rest_bold.json"
    rng = np.random.default_rng(17)
    base = rng.normal(100.0, 5.0, size=(8, 9, 7)).astype(np.float32)
    series = np.stack(
        [base + np.sin(index / 3.0) for index in range(12)],
        axis=3,
    ).astype(np.float32)
    affine = affine if affine is not None else np.diag([3.125, 3.125, 3.5, 1.0])
    image = nib.Nifti1Image(series, affine)
    image.header.set_zooms((3.125, 3.125, 3.5, tr))
    image.header.set_xyzt_units("mm", "sec")
    nib.save(image, path)
    sidecar_metadata = {"RepetitionTime": tr + (0.2 if mismatch else 0.0)}
    if metadata:
        sidecar_metadata.update(metadata)
    sidecar.write_text(json.dumps(sidecar_metadata), encoding="utf-8")
    return path, sidecar


def test_inspect_bold_reports_temporal_geometry_and_tsnr(tmp_path):
    path, sidecar = _write_bold(tmp_path)
    result = inspect_bold(path, sidecar)
    assert result["shape"] == [8, 9, 7, 12]
    assert result["spatial_voxel_sizes_mm"] == [3.125, 3.125, 3.5]
    assert result["header_repetition_time_seconds"] == 2.0
    assert result["sidecar_repetition_time_seconds"] == 2.0
    assert result["repetition_time_matches"] is True
    assert result["median_tsnr"] is not None
    assert result["whole_volume_rms_dvars"]["median"] >= 0
    assert result["automatic_exclusion"] is False


def test_inspect_bold_flags_header_sidecar_tr_mismatch(tmp_path):
    path, sidecar = _write_bold(tmp_path, mismatch=True)
    result = inspect_bold(path, sidecar)
    assert "header_sidecar_repetition_time_mismatch" in result["review_flags"]


def test_inspect_bold_rejects_non_4d_image(tmp_path):
    path = tmp_path / "three_dimensional.nii.gz"
    image = nib.Nifti1Image(np.ones((8, 8, 8), dtype=np.float32), np.eye(4))
    nib.save(image, path)
    sidecar = tmp_path / "three_dimensional.json"
    sidecar.write_text(json.dumps({"RepetitionTime": 2.0}), encoding="utf-8")
    with pytest.raises(ValueError, match="four-dimensional"):
        inspect_bold(path, sidecar)


def test_inspect_bold_computes_power_fd_from_named_motion_columns(tmp_path):
    path, sidecar = _write_bold(tmp_path)
    motion = tmp_path / "motion.tsv"
    columns = [
        "trans_x_mm",
        "trans_y_mm",
        "trans_z_mm",
        "rot_x_rad",
        "rot_y_rad",
        "rot_z_rad",
    ]
    rows = ["\t".join(columns)]
    for index in range(12):
        rows.append(f"{index * 0.1}\t0\t0\t0\t0\t0")
    motion.write_text("\n".join(rows) + "\n", encoding="utf-8")
    result = inspect_bold(path, sidecar, motion_parameters_path=motion)
    assert result["motion"]["mean_mm"] > 0
    assert result["motion"]["max_mm"] == pytest.approx(0.1)


def test_bold_montage_is_written_without_source_modification(tmp_path):
    path, _ = _write_bold(tmp_path)
    output = tmp_path / "private" / "montage.png"
    before = path.read_bytes()
    render_bold_montage(path, output, pseudonym="0123456789abcdef")
    assert output.is_file()
    assert output.stat().st_size > 0
    assert path.read_bytes() == before


def test_aggregate_bold_qc_contains_counts_not_participant_keys():
    records = [
        {
            "participant_key": "private-key-a",
            "orientation_codes": ["L", "A", "S"],
            "review_flags": ["header_sidecar_repetition_time_mismatch"],
            "motion": None,
            "automatic_exclusion": False,
        },
        {
            "participant_key": "private-key-b",
            "orientation_codes": ["L", "A", "S"],
            "review_flags": [],
            "motion": {"mean_mm": 0.1},
            "automatic_exclusion": False,
        },
    ]
    result = aggregate_bold_qc(records)
    assert result["scan_count"] == 2
    assert result["motion_parameter_scan_count"] == 1
    assert "private-key" not in str(result)
    assert result["automatic_exclusion_count"] == 0



def test_inspect_bold_preserves_acquisition_metadata_and_slice_timing(tmp_path):
    path, sidecar = _write_bold(
        tmp_path,
        metadata={
            "PhaseEncodingDirection": "j-",
            "EffectiveEchoSpacing": 0.0005,
            "TotalReadoutTime": 0.0315,
            "ReconMatrixPE": 64,
            "EchoTime": 0.029,
            "TaskName": "rest",
            "MRAcquisitionType": "2D",
            "ScanningSequence": "EP",
            "SequenceName": "*epfid2d1_64",
            "SliceEncodingDirection": "k",
            "SliceTiming": [0.0, 0.5, 1.0, 1.5],
        },
    )
    result = inspect_bold(path, sidecar)
    assert result["PhaseEncodingDirection"] == "j-"
    assert result["EffectiveEchoSpacing"] == pytest.approx(0.0005)
    assert result["TotalReadoutTime"] == pytest.approx(0.0315)
    assert result["ReconMatrixPE"] == 64
    assert result["EchoTime"] == pytest.approx(0.029)
    assert result["TaskName"] == "rest"
    assert result["MRAcquisitionType"] == "2D"
    assert result["ScanningSequence"] == "EP"
    assert result["SequenceName"] == "*epfid2d1_64"
    assert result["SliceEncodingDirection"] == "k"
    assert result["SliceTimingSummary"] == {
        "count": 4,
        "min_seconds": 0.0,
        "median_seconds": 0.75,
        "max_seconds": 1.5,
    }
    assert result["ReadoutTimeConsistency"]["matches"] is True


@pytest.mark.parametrize(
    ("direction", "expected"),
    [
        ("j-", [0.0, -1.0, 0.0]),
        ("i", [1.0, 0.0, 0.0]),
    ],
)
def test_phase_encoding_direction_maps_to_normalized_ras_vector(
    tmp_path,
    direction,
    expected,
):
    path, sidecar = _write_bold(
        tmp_path,
        metadata={"PhaseEncodingDirection": direction},
    )
    result = inspect_bold(path, sidecar)
    assert result["PhaseEncodingVectorRAS"] == pytest.approx(expected)


def test_inspect_bold_rejects_invalid_phase_encoding_direction(tmp_path):
    path, sidecar = _write_bold(
        tmp_path,
        metadata={"PhaseEncodingDirection": "x-"},
    )
    with pytest.raises(ValueError, match="PhaseEncodingDirection"):
        inspect_bold(path, sidecar)


def test_readout_time_consistency_uses_documented_absolute_tolerance(tmp_path):
    path, sidecar = _write_bold(
        tmp_path,
        metadata={
            "EffectiveEchoSpacing": 0.001,
            "TotalReadoutTime": 0.063005,
            "ReconMatrixPE": 64,
        },
    )
    result = inspect_bold(path, sidecar)
    assert result["ReadoutTimeConsistency"]["matches"] is True
    assert result["ReadoutTimeConsistency"]["absolute_tolerance_seconds"] == pytest.approx(
        1e-5
    )

    mismatch_dir = tmp_path / "mismatch"
    mismatch_dir.mkdir()
    path, sidecar = _write_bold(
        mismatch_dir,
        metadata={
            "EffectiveEchoSpacing": 0.001,
            "TotalReadoutTime": 0.064,
            "ReconMatrixPE": 64,
        },
    )
    result = inspect_bold(path, sidecar)
    assert result["ReadoutTimeConsistency"]["matches"] is False
    assert "effective_echo_spacing_total_readout_time_mismatch" in result["review_flags"]


def test_inspect_bold_allows_missing_optional_acquisition_metadata(tmp_path):
    path, sidecar = _write_bold(tmp_path)
    result = inspect_bold(path, sidecar)
    assert result["PhaseEncodingDirection"] is None
    assert result["PhaseEncodingVectorRAS"] is None
    assert result["EffectiveEchoSpacing"] is None
    assert result["TotalReadoutTime"] is None
    assert result["ReconMatrixPE"] is None
    assert result["SliceTimingSummary"] is None
    assert result["ReadoutTimeConsistency"]["matches"] is None


def test_aggregate_bold_qc_reports_phase_encoding_counts_without_identifiers():
    records = [
        {"PhaseEncodingDirection": "j-", "participant_key": "private-a"},
        {"PhaseEncodingDirection": "j-", "participant_key": "private-b"},
        {"PhaseEncodingDirection": "i", "participant_key": "private-c"},
        {"PhaseEncodingDirection": None, "participant_key": "private-d"},
    ]
    result = aggregate_bold_qc(records)
    assert result["phase_encoding_direction_counts"] == {
        "i": 1,
        "j-": 2,
        "missing": 1,
    }
    assert "private-" not in str(result)
