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


def _write_bold(tmp_path, *, tr=2.0, mismatch=False):
    path = tmp_path / "sub-test_task-rest_bold.nii.gz"
    sidecar = tmp_path / "sub-test_task-rest_bold.json"
    rng = np.random.default_rng(17)
    base = rng.normal(100.0, 5.0, size=(8, 9, 7)).astype(np.float32)
    series = np.stack(
        [base + np.sin(index / 3.0) for index in range(12)],
        axis=3,
    ).astype(np.float32)
    affine = np.diag([3.125, 3.125, 3.5, 1.0])
    image = nib.Nifti1Image(series, affine)
    image.header.set_zooms((3.125, 3.125, 3.5, tr))
    nib.save(image, path)
    sidecar.write_text(
        json.dumps({"RepetitionTime": tr + (0.2 if mismatch else 0.0)}),
        encoding="utf-8",
    )
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
