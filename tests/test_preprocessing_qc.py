"""Tests for non-destructive T1w voxel-level QC."""
import nibabel as nib
import numpy as np
import pytest

from src.preprocessing.qc import (
    aggregate_t1w_qc,
    inspect_t1w,
    render_t1w_montage,
)


def _write_t1w(path, *, ndim=3):
    data = np.zeros((12, 14, 16), dtype=np.float32)
    data[2:10, 3:12, 4:14] = 20.0
    if ndim == 3:
        data[0, 0, 0] = np.nan
    if ndim == 4:
        data = np.repeat(data[..., np.newaxis], 2, axis=3)
    image = nib.Nifti1Image(data, np.diag([1.0, 1.0, 1.0, 1.0]))
    nib.save(image, path)


def test_inspect_t1w_reports_voxel_metrics_and_flags_nonfinite(tmp_path):
    path = tmp_path / "synthetic_T1w.nii.gz"
    _write_t1w(path)
    result = inspect_t1w(
        path,
        thresholds={
            "max_nonfinite_fraction": 0.0,
            "max_zero_fraction": 0.9,
            "min_nonzero_fraction": 0.1,
            "min_dynamic_range": 1.0,
        },
    )
    assert result["shape"] == [12, 14, 16]
    assert result["orientation_codes"] == ["R", "A", "S"]
    assert result["nonfinite_voxel_count"] == 1
    assert "nonfinite_voxels" in result["review_flags"]
    assert result["automatic_exclusion"] is False
    assert result["foreground_is_brain_mask"] is False


def test_inspect_t1w_rejects_non_3d_image(tmp_path):
    path = tmp_path / "synthetic_bold.nii.gz"
    _write_t1w(path, ndim=4)
    with pytest.raises(ValueError, match="three-dimensional"):
        inspect_t1w(path)


def test_inspect_t1w_rejects_unknown_threshold(tmp_path):
    path = tmp_path / "synthetic_T1w.nii.gz"
    _write_t1w(path)
    with pytest.raises(ValueError, match="Unknown T1w QC threshold"):
        inspect_t1w(path, thresholds={"brain_volume_ml": 100.0})


def test_montage_is_written_without_source_modification(tmp_path):
    path = tmp_path / "synthetic_T1w.nii.gz"
    output = tmp_path / "private" / "montage.png"
    _write_t1w(path)
    before = path.read_bytes()
    render_t1w_montage(path, output, pseudonym="0123456789abcdef")
    assert output.is_file()
    assert output.stat().st_size > 0
    assert path.read_bytes() == before


def test_aggregate_qc_contains_counts_not_participant_ids():
    records = [
        {
            "participant_key": "private-key-a",
            "orientation_codes": ["R", "A", "S"],
            "review_flags": ["nonfinite_voxels"],
            "automatic_exclusion": False,
        },
        {
            "participant_key": "private-key-b",
            "orientation_codes": ["L", "A", "S"],
            "review_flags": ["nonfinite_voxels", "high_zero_fraction"],
            "automatic_exclusion": False,
        },
    ]
    result = aggregate_t1w_qc(records)
    rendered = str(result)
    assert result["scan_count"] == 2
    assert result["review_flag_counts"] == {
        "high_zero_fraction": 1,
        "nonfinite_voxels": 2,
    }
    assert "private-key" not in rendered
    assert result["automatic_exclusion_count"] == 0


def test_inspect_t1w_flags_singular_affine_without_crashing(tmp_path):
    path = tmp_path / "singular_T1w.nii.gz"
    data = np.ones((8, 8, 8), dtype=np.float32)
    affine = np.diag([1.0, 1.0, 0.0, 1.0])
    nib.save(nib.Nifti1Image(data, affine), path)
    result = inspect_t1w(path)
    assert "invalid_affine_determinant" in result["review_flags"]
