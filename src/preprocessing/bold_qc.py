"""First-pass temporal and geometry QC for resting-state BOLD MRI.

This module does not estimate or correct head motion. If motion estimates are
provided, they must use the explicit six-column TSV contract documented below.
Whole-volume DVARS is a coarse temporal-change metric, not standardized DVARS.
"""
from __future__ import annotations

import csv
import json
from collections import Counter
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np

_ALLOWED_THRESHOLDS = {
    "max_nonfinite_fraction",
    "max_zero_fraction",
    "min_tsnr_median",
    "max_dvars_p95",
    "max_fd_mean_mm",
    "max_fd_p95_mm",
}
_MOTION_COLUMNS = (
    "trans_x_mm",
    "trans_y_mm",
    "trans_z_mm",
    "rot_x_rad",
    "rot_y_rad",
    "rot_z_rad",
)
_HEAD_RADIUS_MM = 50.0


def _validate_thresholds(thresholds: Mapping[str, float]) -> None:
    unknown = set(thresholds) - _ALLOWED_THRESHOLDS
    if unknown:
        raise ValueError(f"Unknown BOLD QC threshold names: {sorted(unknown)}")
    for name, value in thresholds.items():
        if not np.isfinite(value):
            raise ValueError(f"BOLD QC threshold must be finite: {name}")
        if name.endswith("_fraction") and not 0.0 <= value <= 1.0:
            raise ValueError(f"BOLD QC fraction threshold must be in [0, 1]: {name}")
        if name.startswith("min_") and value < 0:
            raise ValueError(f"BOLD QC minimum threshold must be non-negative: {name}")
        if name.startswith("max_") and value < 0:
            raise ValueError(f"BOLD QC maximum threshold must be non-negative: {name}")


def _read_motion_parameters(path: str | Path, n_volumes: int) -> np.ndarray:
    """Read a TSV with translations in mm and rotations in radians.

    Required columns: trans_x_mm, trans_y_mm, trans_z_mm, rot_x_rad,
    rot_y_rad, rot_z_rad. Rows must correspond one-to-one with BOLD volumes.
    """
    source = Path(path)
    if not source.is_file():
        raise FileNotFoundError("Motion parameter TSV does not exist")
    with source.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        if not reader.fieldnames or not set(_MOTION_COLUMNS).issubset(reader.fieldnames):
            raise ValueError("Motion TSV is missing one or more required named columns")
        rows = list(reader)
    if len(rows) != n_volumes:
        raise ValueError("Motion parameter row count must equal BOLD volume count")
    try:
        values = np.asarray(
            [[float(row[column]) for column in _MOTION_COLUMNS] for row in rows],
            dtype=np.float64,
        )
    except (TypeError, ValueError) as exc:
        raise ValueError("Motion parameters must contain numeric values") from exc
    if not np.isfinite(values).all():
        raise ValueError("Motion parameters must all be finite")
    return values


def _power_fd(parameters: np.ndarray) -> np.ndarray:
    """Compute Power FD using a 50 mm head radius."""
    differences = np.diff(parameters, axis=0)
    fd = np.zeros(parameters.shape[0], dtype=np.float64)
    if differences.size:
        fd[1:] = (
            np.abs(differences[:, :3]).sum(axis=1)
            + _HEAD_RADIUS_MM * np.abs(differences[:, 3:]).sum(axis=1)
        )
    return fd


def inspect_bold(
    image_path: str | Path,
    sidecar_path: str | Path,
    *,
    motion_parameters_path: str | Path | None = None,
    thresholds: Mapping[str, float] | None = None,
) -> dict[str, Any]:
    """Compute first-pass BOLD QC without modifying the source image."""
    path = Path(image_path)
    sidecar = Path(sidecar_path)
    if not path.is_file():
        raise FileNotFoundError("BOLD image file does not exist")
    if not sidecar.is_file():
        raise FileNotFoundError("BOLD JSON sidecar does not exist")
    limits = dict(thresholds or {})
    _validate_thresholds(limits)

    metadata = json.loads(sidecar.read_text(encoding="utf-8"))
    if not isinstance(metadata, dict):
        raise TypeError("BOLD sidecar must contain a JSON object")
    sidecar_tr = metadata.get("RepetitionTime")
    if isinstance(sidecar_tr, bool) or not isinstance(sidecar_tr, (int, float)):
        raise TypeError("BOLD sidecar requires numeric RepetitionTime in seconds")
    sidecar_tr = float(sidecar_tr)
    if not np.isfinite(sidecar_tr) or sidecar_tr <= 0:
        raise ValueError("BOLD sidecar RepetitionTime must be finite and positive")

    image = nib.load(str(path))
    if len(image.shape) != 4:
        raise ValueError("BOLD image must be four-dimensional")
    x_size, y_size, z_size, n_volumes = (int(value) for value in image.shape)
    if n_volumes < 2:
        raise ValueError("BOLD image must contain at least two time points")
    zooms = image.header.get_zooms()
    spatial_zooms = np.asarray(zooms[:3], dtype=np.float64)
    header_tr_raw = float(zooms[3])
    _, temporal_unit = image.header.get_xyzt_units()
    temporal_factors = {"sec": 1.0, "msec": 1e-3, "usec": 1e-6}
    header_tr = (
        header_tr_raw * temporal_factors[temporal_unit]
        if temporal_unit in temporal_factors
        else None
    )
    if not np.isfinite(spatial_zooms).all() or np.any(spatial_zooms <= 0):
        raise ValueError("BOLD spatial voxel sizes must be finite and positive")
    if header_tr is not None and (not np.isfinite(header_tr) or header_tr <= 0):
        raise ValueError("BOLD NIfTI temporal spacing must be finite and positive")

    data = image.get_fdata(dtype=np.float32)
    total_voxels = int(data.size)
    finite = np.isfinite(data)
    finite_fraction = float(np.count_nonzero(finite) / total_voxels)
    nonfinite_fraction = 1.0 - finite_fraction
    zero_fraction = float(np.count_nonzero(finite & (data == 0)) / total_voxels)
    spatial_mask = np.any(finite & (data != 0), axis=3)

    # Per-voxel temporal SNR; only finite, nonzero-foreground voxels with
    # positive temporal mean and nonzero temporal SD contribute.
    finite_all_time = np.all(finite, axis=3) & spatial_mask
    tsnr_values = np.asarray([], dtype=np.float32)
    if np.any(finite_all_time):
        selected = data[finite_all_time]
        temporal_mean = selected.mean(axis=1)
        temporal_sd = selected.std(axis=1, ddof=1)
        valid_tsnr = (temporal_mean > 0) & (temporal_sd > 0)
        if np.any(valid_tsnr):
            tsnr_values = temporal_mean[valid_tsnr] / temporal_sd[valid_tsnr]

    # Whole-volume RMS temporal difference on the nonzero foreground proxy.
    # This is deliberately not called standardized DVARS and is not brain-masked.
    dvars_values: list[float] = []
    global_means: list[float] = []
    for index in range(n_volumes):
        frame = data[..., index]
        valid_frame = spatial_mask & finite[..., index]
        if np.any(valid_frame):
            global_means.append(float(np.mean(frame[valid_frame])))
        else:
            global_means.append(float("nan"))
        if index == 0:
            continue
        valid_pair = spatial_mask & finite[..., index - 1] & finite[..., index]
        if np.any(valid_pair):
            difference = data[..., index][valid_pair] - data[..., index - 1][valid_pair]
            dvars_values.append(float(np.sqrt(np.mean(np.square(difference)))))

    dvars = np.asarray(dvars_values, dtype=np.float64)
    finite_global = np.asarray(global_means, dtype=np.float64)
    finite_global = finite_global[np.isfinite(finite_global)]
    global_mean_cv_percent = None
    if finite_global.size > 1 and abs(float(np.mean(finite_global))) > 1e-12:
        global_mean_cv_percent = float(
            100.0 * np.std(finite_global, ddof=1) / abs(np.mean(finite_global))
        )

    motion_metrics = None
    if motion_parameters_path is not None:
        parameters = _read_motion_parameters(motion_parameters_path, n_volumes)
        fd = _power_fd(parameters)
        motion_metrics = {
            "definition": "Power FD; translations in mm, rotations in radians, 50 mm radius",
            "mean_mm": float(np.mean(fd)),
            "median_mm": float(np.median(fd)),
            "p95_mm": float(np.percentile(fd, 95)),
            "max_mm": float(np.max(fd)),
            "fraction_over_0_5_mm": float(np.mean(fd > 0.5)),
        }

    affine = np.asarray(image.affine, dtype=np.float64)
    affine_finite = bool(np.isfinite(affine).all())
    determinant = float(np.linalg.det(affine[:3, :3])) if affine_finite else float("nan")
    if affine_finite:
        orientation = nib.aff2axcodes(affine)
    else:
        orientation = (None, None, None)
    tr_difference = abs(header_tr - sidecar_tr)
    flags: list[str] = []
    if nonfinite_fraction > limits.get("max_nonfinite_fraction", 0.0):
        flags.append("nonfinite_voxels")
    if abs(determinant) <= 1e-8 or not np.isfinite(determinant):
        flags.append("invalid_affine_determinant")
    if header_tr is None:
        flags.append("unknown_nifti_temporal_unit")
    elif tr_difference > 0.001:
        flags.append("header_sidecar_repetition_time_mismatch")
    if "max_zero_fraction" in limits and zero_fraction > limits["max_zero_fraction"]:
        flags.append("high_zero_fraction")
    if (
        "min_tsnr_median" in limits
        and tsnr_values.size
        and float(np.median(tsnr_values)) < limits["min_tsnr_median"]
    ):
        flags.append("low_median_tsnr")
    if (
        "max_dvars_p95" in limits
        and dvars.size
        and float(np.percentile(dvars, 95)) > limits["max_dvars_p95"]
    ):
        flags.append("high_whole_volume_dvars_p95")
    if motion_metrics is not None:
        if "max_fd_mean_mm" in limits and motion_metrics["mean_mm"] > limits["max_fd_mean_mm"]:
            flags.append("high_mean_framewise_displacement")
        if "max_fd_p95_mm" in limits and motion_metrics["p95_mm"] > limits["max_fd_p95_mm"]:
            flags.append("high_p95_framewise_displacement")

    def summary(values: np.ndarray) -> dict[str, float] | None:
        if values.size == 0:
            return None
        return {
            "median": float(np.median(values)),
            "p95": float(np.percentile(values, 95)),
            "max": float(np.max(values)),
        }

    return {
        "shape": [x_size, y_size, z_size, n_volumes],
        "spatial_voxel_sizes_mm": [round(float(value), 6) for value in spatial_zooms],
        "orientation_codes": list(orientation),
        "affine_determinant": round(determinant, 8) if np.isfinite(determinant) else None,
        "header_repetition_time_seconds": header_tr,
        "nifti_temporal_unit": temporal_unit,
        "sidecar_repetition_time_seconds": sidecar_tr,
        "repetition_time_absolute_difference_seconds": tr_difference,
        "repetition_time_matches": (
            tr_difference <= 0.001 if tr_difference is not None else None
        ),
        "volume_count": n_volumes,
        "duration_seconds": float(n_volumes * sidecar_tr),
        "nonfinite_voxel_count": int(total_voxels - np.count_nonzero(finite)),
        "nonfinite_fraction": nonfinite_fraction,
        "zero_fraction": zero_fraction,
        "nonzero_foreground_fraction": float(np.count_nonzero(spatial_mask) / spatial_mask.size),
        "median_tsnr": float(np.median(tsnr_values)) if tsnr_values.size else None,
        "tsnr_voxel_count": int(tsnr_values.size),
        "whole_volume_rms_dvars": summary(dvars),
        "global_mean_signal_cv_percent": global_mean_cv_percent,
        "motion": motion_metrics,
        "review_flags": flags,
        "automatic_exclusion": False,
        "foreground_note": "Nonzero foreground proxy includes non-brain tissue and is not a brain mask.",
        "dvars_note": "Whole-volume RMS temporal differences are not standardized or brain-masked DVARS.",
    }


def render_bold_montage(
    image_path: str | Path,
    output_path: str | Path,
    *,
    pseudonym: str,
) -> None:
    """Save mean-BOLD, temporal-SNR and global-signal review panels."""
    image = nib.load(str(image_path))
    data = image.get_fdata(dtype=np.float32)
    if data.ndim != 4:
        raise ValueError("BOLD montage requires a four-dimensional image")
    finite = np.isfinite(data)
    count = finite.sum(axis=3)
    total = np.where(finite, data, 0.0).sum(axis=3)
    mean_image = np.divide(total, count, out=np.zeros_like(total), where=count > 0)
    complete = np.all(finite, axis=3)
    temporal_sd = data.std(axis=3, ddof=1)
    tsnr = np.divide(
        mean_image,
        temporal_sd,
        out=np.zeros_like(mean_image),
        where=complete & (temporal_sd > 0),
    )
    spatial_mask = np.any(finite & (data != 0), axis=3)
    signal = []
    for index in range(data.shape[3]):
        valid = spatial_mask & finite[..., index]
        signal.append(float(np.mean(data[..., index][valid])) if np.any(valid) else float("nan"))

    z = data.shape[2] // 2
    codes = nib.aff2axcodes(image.affine)
    orientation = "".join(str(code) for code in codes if code) or "unknown"
    figure, axes = plt.subplots(2, 2, figsize=(10, 8))
    figure.suptitle(f"BOLD native voxel orientation: {orientation} | {pseudonym}")
    axes[0, 0].imshow(mean_image[:, :, z].T, cmap="gray", origin="lower")
    axes[0, 0].set_title("Temporal mean, axial center")
    axes[0, 1].imshow(tsnr[:, :, z].T, cmap="viridis", origin="lower")
    axes[0, 1].set_title("Temporal SNR proxy, axial center")
    axes[1, 0].plot(signal)
    axes[1, 0].set_title("Whole-volume nonzero-foreground mean")
    axes[1, 0].set_xlabel("Volume")
    axes[1, 0].set_ylabel("Mean stored intensity")
    axes[1, 1].hist(mean_image[spatial_mask], bins=100)
    axes[1, 1].set_title("Temporal-mean intensity distribution")
    figure.tight_layout()
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(destination, dpi=130, bbox_inches="tight")
    plt.close(figure)


def aggregate_bold_qc(records: list[Mapping[str, Any]]) -> dict[str, Any]:
    """Summarize BOLD QC without participant identifiers or file paths."""
    flag_counts: Counter[str] = Counter()
    orientation_counts: Counter[str] = Counter()
    motion_available = 0
    automatic_exclusions = 0
    for record in records:
        flag_counts.update(record.get("review_flags", []))
        codes = record.get("orientation_codes") or []
        orientation = "".join(str(code) for code in codes if code)
        orientation_counts.update([orientation or "unknown"])
        motion_available += record.get("motion") is not None
        automatic_exclusions += bool(record.get("automatic_exclusion", False))
    return {
        "scan_count": len(records),
        "review_flag_counts": dict(sorted(flag_counts.items())),
        "orientation_counts": dict(sorted(orientation_counts.items())),
        "motion_parameter_scan_count": motion_available,
        "automatic_exclusion_count": automatic_exclusions,
        "participant_level_identifiers_emitted": False,
        "source_images_modified": False,
    }
