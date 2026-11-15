"""Voxel-level structural MRI QC metrics and private visual montages.

The foreground proxy is not a brain mask. This module flags scans for review;
it never automatically excludes or modifies source images.
"""
from __future__ import annotations

from collections import Counter
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import matplotlib
import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np

matplotlib.use("Agg")

_ALLOWED_THRESHOLDS = {
    "max_nonfinite_fraction",
    "max_zero_fraction",
    "min_nonzero_fraction",
    "min_dynamic_range",
}


def _validate_thresholds(thresholds: Mapping[str, float]) -> None:
    unknown = set(thresholds) - _ALLOWED_THRESHOLDS
    if unknown:
        raise ValueError(f"Unknown T1w QC threshold names: {sorted(unknown)}")
    for name, value in thresholds.items():
        if not np.isfinite(value):
            raise ValueError(f"T1w QC threshold must be finite: {name}")
        if name.endswith("_fraction") and not 0.0 <= value <= 1.0:
            raise ValueError(f"T1w QC fraction threshold must be in [0, 1]: {name}")
        if name == "min_dynamic_range" and value < 0:
            raise ValueError("min_dynamic_range must be non-negative")


def inspect_t1w(
    image_path: str | Path,
    *,
    thresholds: Mapping[str, float] | None = None,
) -> dict[str, Any]:
    """Compute image-level T1w metrics without changing the source image.

    Thresholds are supplied by the research protocol/configuration. No
    population-derived cutoff is estimated from the full cohort.
    """
    path = Path(image_path)
    if not path.is_file():
        raise FileNotFoundError("T1w image file does not exist")
    limits = dict(thresholds or {})
    _validate_thresholds(limits)

    image = nib.load(str(path))
    data = image.get_fdata(dtype=np.float32)
    if data.ndim != 3:
        raise ValueError("T1w image must be three-dimensional")
    total_voxels = int(data.size)
    finite_mask = np.isfinite(data)
    finite_values = data[finite_mask]
    if finite_values.size == 0:
        raise ValueError("T1w image contains no finite voxel values")

    percentiles = np.percentile(finite_values, [0.5, 1, 50, 99, 99.5])
    nonzero_mask = finite_mask & (data != 0)
    nonzero_count = int(np.count_nonzero(nonzero_mask))
    nonzero_fraction = nonzero_count / total_voxels
    zero_fraction = int(np.count_nonzero(finite_mask & (data == 0))) / total_voxels
    nonfinite_fraction = 1.0 - (int(np.count_nonzero(finite_mask)) / total_voxels)
    dynamic_range = float(percentiles[3] - percentiles[1])

    foreground_bounds = None
    if nonzero_count:
        coordinates = np.where(nonzero_mask)
        foreground_bounds = [
            [int(axis.min()), int(axis.max()) + 1] for axis in coordinates
        ]

    affine = np.asarray(image.affine, dtype=np.float64)
    determinant = float(np.linalg.det(affine[:3, :3]))
    axcodes = nib.aff2axcodes(affine)
    voxel_sizes = nib.affines.voxel_sizes(affine)
    flags: list[str] = []
    if nonfinite_fraction > limits.get("max_nonfinite_fraction", 0.0):
        flags.append("nonfinite_voxels")
    if "max_zero_fraction" in limits and zero_fraction > limits["max_zero_fraction"]:
        flags.append("high_zero_fraction")
    if "min_nonzero_fraction" in limits and nonzero_fraction < limits["min_nonzero_fraction"]:
        flags.append("low_nonzero_fraction")
    if "min_dynamic_range" in limits and dynamic_range < limits["min_dynamic_range"]:
        flags.append("low_intensity_dynamic_range")
    if not np.isfinite(determinant) or abs(determinant) <= 1e-8:
        flags.append("invalid_affine_determinant")

    return {
        "shape": [int(value) for value in data.shape],
        "voxel_sizes_mm": [round(float(value), 6) for value in voxel_sizes],
        "orientation_codes": list(axcodes),
        "affine_determinant": round(determinant, 8) if np.isfinite(determinant) else None,
        "voxel_count": total_voxels,
        "nonfinite_voxel_count": int(total_voxels - np.count_nonzero(finite_mask)),
        "nonfinite_fraction": round(nonfinite_fraction, 8),
        "zero_fraction": round(zero_fraction, 8),
        "nonzero_fraction": round(nonzero_fraction, 8),
        "intensity_percentiles": {
            "p0_5": float(percentiles[0]),
            "p1": float(percentiles[1]),
            "p50": float(percentiles[2]),
            "p99": float(percentiles[3]),
            "p99_5": float(percentiles[4]),
        },
        "p99_minus_p1_dynamic_range": dynamic_range,
        "nonzero_foreground_bounds_voxels": foreground_bounds,
        "foreground_is_brain_mask": False,
        "review_flags": flags,
        "automatic_exclusion": False,
    }


def render_t1w_montage(
    image_path: str | Path,
    output_path: str | Path,
    *,
    pseudonym: str,
) -> None:
    """Save native-orientation center slices and intensity histogram."""
    image = nib.load(str(image_path))
    data = image.get_fdata(dtype=np.float32)
    if data.ndim != 3:
        raise ValueError("T1w montage requires a three-dimensional image")
    finite = data[np.isfinite(data)]
    if finite.size == 0:
        raise ValueError("T1w image contains no finite voxel values")
    low, high = np.percentile(finite, [1, 99])
    if not high > low:
        low = float(finite.min())
        high = float(finite.max())
    if not high > low:
        high = low + 1.0

    x, y, z = (dimension // 2 for dimension in data.shape)
    axcodes = "".join(str(code) for code in nib.aff2axcodes(image.affine))
    figure, axes = plt.subplots(2, 2, figsize=(10, 8))
    figure.suptitle(f"T1w native voxel orientation: {axcodes} | {pseudonym}")
    panels = (
        (axes[0, 0], data[:, :, z].T, "Axial center slice"),
        (axes[0, 1], data[:, y, :].T, "Coronal center slice"),
        (axes[1, 0], data[x, :, :].T, "Sagittal center slice"),
    )
    for axis, panel, title in panels:
        axis.imshow(panel, cmap="gray", origin="lower", vmin=low, vmax=high)
        axis.set_title(title)
        axis.axis("off")
    axes[1, 1].hist(finite, bins=100)
    axes[1, 1].set_title("Finite voxel intensity distribution")
    axes[1, 1].set_xlabel("Stored intensity")
    axes[1, 1].set_ylabel("Voxel count")
    figure.tight_layout()
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(destination, dpi=130, bbox_inches="tight")
    plt.close(figure)


def aggregate_t1w_qc(records: list[Mapping[str, Any]]) -> dict[str, Any]:
    """Summarize QC flags without emitting participant IDs or image paths."""
    flag_counts: Counter[str] = Counter()
    orientation_counts: Counter[str] = Counter()
    invalid = 0
    for record in records:
        flag_counts.update(record.get("review_flags", []))
        orientation_counts.update(["".join(record.get("orientation_codes", []))])
        invalid += bool(record.get("automatic_exclusion", False))
    return {
        "scan_count": len(records),
        "review_flag_counts": dict(sorted(flag_counts.items())),
        "orientation_counts": dict(sorted(orientation_counts.items())),
        "automatic_exclusion_count": invalid,
        "participant_level_identifiers_emitted": False,
        "voxel_data_modified": False,
        "foreground_mask_note": "Nonzero foreground bounds are not a brain mask or brain-volume estimate.",
    }
