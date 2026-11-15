"""Metadata-only BIDS inventory and NIfTI-1 geometry validation.

Reads BIDS tables, selected JSON sidecar fields and NIfTI-1 headers. It never
loads voxel arrays and emits aggregate summaries only.
"""
from __future__ import annotations

import csv
import gzip
import itertools
import json
import math
import struct
from collections import Counter, defaultdict
from pathlib import Path
from typing import BinaryIO

from src.data.inventory import sha256_file

MODALITY_PATTERNS = {"T1w": "*_T1w.nii*", "bold": "*_bold.nii*"}
SIDECAR_KEYS = (
    "Manufacturer", "ManufacturersModelName", "MagneticFieldStrength",
    "RepetitionTime", "EchoTime", "FlipAngle", "PhaseEncodingDirection",
    "TotalReadoutTime", "SliceTiming",
)
_AXIS_LABELS = (("L", "R"), ("P", "A"), ("I", "S"))
_AXIS_PERMUTATIONS = tuple(itertools.permutations(range(3)))


def _open_nifti(path: Path) -> BinaryIO:
    return gzip.open(path, "rb") if path.name.endswith(".gz") else path.open("rb")


def _orientation_codes(affine: list[list[float]]) -> list[str] | None:
    """Return closest RAS+ anatomical axis code for each voxel axis."""
    columns = [[affine[row][col] for row in range(3)] for col in range(3)]
    norms = [math.sqrt(sum(value * value for value in col)) for col in columns]
    if any(not math.isfinite(norm) or norm <= 1e-8 for norm in norms):
        return None
    unit = [[value / norms[i] for value in columns[i]] for i in range(3)]
    best: tuple[float, tuple[int, ...]] | None = None
    for assignment in _AXIS_PERMUTATIONS:
        score = sum(abs(unit[assignment[world]][world]) for world in range(3))
        if best is None or score > best[0]:
            best = (score, assignment)
    if best is None or best[0] < 2.0:
        return None
    result = []
    for voxel_axis, world_axis in enumerate(best[1]):
        sign = unit[voxel_axis][world_axis]
        result.append(_AXIS_LABELS[world_axis][1 if sign >= 0 else 0])
    return result


def _qform_affine(header: bytes, endian: str, pixdim: tuple[float, ...]) -> list[list[float]]:
    b, c, d = struct.unpack_from(f"{endian}3f", header, 256)
    x, y, z = struct.unpack_from(f"{endian}3f", header, 268)
    norm = b * b + c * c + d * d
    if norm > 1.0:
        scale = 1.0 / math.sqrt(norm)
        b, c, d = b * scale, c * scale, d * scale
        a = 0.0
    else:
        a = math.sqrt(max(0.0, 1.0 - norm))
    rotation = [
        [a*a+b*b-c*c-d*d, 2*b*c-2*a*d, 2*b*d+2*a*c],
        [2*b*c+2*a*d, a*a+c*c-b*b-d*d, 2*c*d-2*a*b],
        [2*b*d-2*a*c, 2*c*d+2*a*b, a*a+d*d-c*c-b*b],
    ]
    scales = [abs(pixdim[i]) for i in (1, 2, 3)]
    if pixdim[0] < 0:
        scales[2] *= -1
    return [
        [rotation[row][col] * scales[col] for col in range(3)] + [offset]
        for row, offset in enumerate((x, y, z))
    ] + [[0.0, 0.0, 0.0, 1.0]]


def _determinant3(matrix: list[list[float]]) -> float:
    a, b, c = matrix
    return (
        a[0] * (b[1] * c[2] - b[2] * c[1])
        - a[1] * (b[0] * c[2] - b[2] * c[0])
        + a[2] * (b[0] * c[1] - b[1] * c[0])
    )


def read_nifti_header(path: str | Path) -> dict[str, object]:
    """Read NIfTI-1 dimensions, spatial/time spacing and coded affine metadata."""
    file_path = Path(path)
    with _open_nifti(file_path) as stream:
        header = stream.read(348)
    if len(header) != 348:
        raise ValueError(f"Truncated NIfTI-1 header: {file_path.name}")
    little = struct.unpack_from("<i", header, 0)[0]
    big = struct.unpack_from(">i", header, 0)[0]
    if little == 348:
        endian = "<"
    elif big == 348:
        endian = ">"
    else:
        raise ValueError(f"Invalid NIfTI-1 header size: {file_path.name}")
    dims = struct.unpack_from(f"{endian}8h", header, 40)
    pixdim = struct.unpack_from(f"{endian}8f", header, 76)
    ndim = dims[0]
    if ndim < 1 or ndim > 7 or any(value <= 0 for value in dims[1 : ndim + 1]):
        raise ValueError(f"Invalid NIfTI dimensions: {file_path.name}")
    if any(not math.isfinite(value) or value <= 0 for value in pixdim[1:4]):
        raise ValueError(f"Invalid NIfTI spatial voxel spacing: {file_path.name}")
    if ndim >= 4 and (not math.isfinite(pixdim[4]) or pixdim[4] <= 0):
        raise ValueError(f"Invalid NIfTI temporal spacing: {file_path.name}")

    datatype = struct.unpack_from(f"{endian}h", header, 70)[0]
    bitpix = struct.unpack_from(f"{endian}h", header, 72)[0]
    qform_code, sform_code = struct.unpack_from(f"{endian}2h", header, 252)
    qform = _qform_affine(header, endian, pixdim) if qform_code > 0 else None
    srows = struct.unpack_from(f"{endian}12f", header, 280)
    sform = (
        [list(srows[0:4]), list(srows[4:8]), list(srows[8:12]), [0.0, 0.0, 0.0, 1.0]]
        if sform_code > 0 else None
    )
    affine_source = "sform" if sform is not None else "qform" if qform is not None else "fallback"
    affine = sform or qform or [
        [abs(pixdim[1]), 0.0, 0.0, 0.0],
        [0.0, abs(pixdim[2]), 0.0, 0.0],
        [0.0, 0.0, abs(pixdim[3]) * (-1.0 if pixdim[0] < 0 else 1.0), 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ]
    linear = [row[:3] for row in affine[:3]]
    determinant = _determinant3(linear)
    finite_affine = all(math.isfinite(value) for row in affine for value in row)
    valid_affine = finite_affine and math.isfinite(determinant) and abs(determinant) > 1e-8
    orientation = _orientation_codes(affine) if valid_affine and affine_source != "fallback" else None
    qform_sform_max_abs_difference = None
    if qform is not None and sform is not None:
        qform_sform_max_abs_difference = round(
            max(abs(qform[r][c] - sform[r][c]) for r in range(4) for c in range(4)), 6
        )
    return {
        "ndim": ndim,
        "shape": list(dims[1 : ndim + 1]),
        "spatial_voxel_sizes_mm": [round(abs(pixdim[i]), 5) for i in (1, 2, 3)],
        "header_time_spacing_seconds": round(pixdim[4], 6) if ndim >= 4 else None,
        "datatype": datatype,
        "bitpix": bitpix,
        "qform_code": qform_code,
        "sform_code": sform_code,
        "affine_source": affine_source,
        "affine_determinant": round(determinant, 8) if math.isfinite(determinant) else None,
        "affine_valid": valid_affine,
        "orientation_codes": orientation,
        "qform_sform_max_abs_difference": qform_sform_max_abs_difference,
    }


def _read_participants(path: Path) -> dict[str, str]:
    if not path.is_file():
        raise FileNotFoundError(f"Missing BIDS participants.tsv: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        if not reader.fieldnames or not {"participant_id", "group"}.issubset(reader.fieldnames):
            raise ValueError("participants.tsv must contain participant_id and group")
        rows = list(reader)
    ids = [row["participant_id"].strip() for row in rows]
    if any(not value for value in ids):
        raise ValueError("participants.tsv contains an empty participant_id")
    if len(ids) != len(set(ids)):
        raise ValueError("participants.tsv contains duplicate participant_id values")
    return {row["participant_id"].strip(): row["group"].strip() for row in rows}


def _sidecar(path: Path) -> dict[str, object]:
    sidecar = path.with_suffix("").with_suffix(".json") if path.name.endswith(".nii.gz") else path.with_suffix(".json")
    if not sidecar.is_file():
        return {}
    try:
        payload = json.loads(sidecar.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ValueError(f"Invalid BIDS JSON sidecar: {sidecar.name}") from exc
    if not isinstance(payload, dict):
        raise TypeError(f"BIDS JSON sidecar must contain an object: {sidecar.name}")
    return {key: payload[key] for key in SIDECAR_KEYS if key in payload}


def inventory_bids_dataset(root: str | Path) -> dict[str, object]:
    """Return aggregate-only participant/modality and NIfTI metadata summaries."""
    base = Path(root)
    if not base.is_dir():
        raise NotADirectoryError(f"BIDS root is not a directory: {base}")
    description_path = base / "dataset_description.json"
    if not description_path.is_file():
        raise FileNotFoundError(f"Missing BIDS dataset_description.json: {description_path}")
    try:
        description = json.loads(description_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ValueError("Invalid BIDS dataset_description.json") from exc
    if not isinstance(description, dict):
        raise TypeError("dataset_description.json must contain an object")
    participants_path = base / "participants.tsv"
    participants = _read_participants(participants_path)
    groups = Counter(participants.values())
    files_by_modality: dict[str, dict[str, list[Path]]] = {
        modality: defaultdict(list) for modality in MODALITY_PATTERNS
    }
    for modality, pattern in MODALITY_PATTERNS.items():
        for path in sorted(base.rglob(pattern)):
            if path.is_file():
                parts = path.relative_to(base).parts
                if any(part.startswith(".") for part in parts):
                    continue
                subject_dirs = [part for part in parts if part.startswith("sub-")]
                if subject_dirs:
                    files_by_modality[modality][subject_dirs[0]].append(path)

    modality_summary: dict[str, object] = {}
    for modality, by_subject in files_by_modality.items():
        known = set(by_subject) & set(participants)
        unknown = set(by_subject) - set(participants)
        group_coverage = Counter(participants[subject] for subject in known)
        headers: list[dict[str, object]] = []
        sidecar_fields: Counter[str] = Counter()
        repetition_times: Counter[str] = Counter()
        invalid_headers = 0
        invalid_affines = 0
        missing_affine_codes = 0
        orientation_counts: Counter[str] = Counter()
        qform_sform_disagreements = 0
        missing_sidecars = 0
        for subject_files in by_subject.values():
            for image_path in subject_files:
                try:
                    item = read_nifti_header(image_path)
                    headers.append(item)
                    invalid_affines += not bool(item["affine_valid"])
                    missing_affine_codes += item["affine_source"] == "fallback"
                    if item["orientation_codes"]:
                        orientation_counts.update(["".join(item["orientation_codes"])])
                    if item["qform_sform_max_abs_difference"] is not None and item["qform_sform_max_abs_difference"] > 1e-3:
                        qform_sform_disagreements += 1
                except (OSError, ValueError, EOFError, struct.error):
                    invalid_headers += 1
                metadata = _sidecar(image_path)
                if not metadata:
                    missing_sidecars += 1
                sidecar_fields.update(metadata.keys())
                tr = metadata.get("RepetitionTime")
                if isinstance(tr, (int, float)) and math.isfinite(tr):
                    repetition_times.update([str(round(float(tr), 6))])
        shape_counts = Counter(tuple(item["shape"]) for item in headers)
        spacing_counts = Counter(tuple(item["spatial_voxel_sizes_mm"]) for item in headers)
        header_tr_counts = Counter(
            str(item["header_time_spacing_seconds"]) for item in headers
            if item["header_time_spacing_seconds"] is not None
        )
        modality_summary[modality] = {
            "file_count": sum(len(paths) for paths in by_subject.values()),
            "participant_count": len(known),
            "participant_count_by_group": dict(sorted(group_coverage.items())),
            "participants_without_file_count": len(set(participants) - known),
            "files_for_unknown_participant_count": sum(len(by_subject[s]) for s in unknown),
            "invalid_nifti_header_count": invalid_headers,
            "invalid_affine_count": invalid_affines,
            "missing_coded_affine_count": missing_affine_codes,
            "orientation_code_counts": dict(sorted(orientation_counts.items())),
            "qform_sform_disagreement_count": qform_sform_disagreements,
            "missing_or_empty_sidecar_count": missing_sidecars,
            "header_shape_counts": {str(k): v for k, v in sorted(shape_counts.items())},
            "spatial_voxel_spacing_mm_counts": {str(k): v for k, v in sorted(spacing_counts.items())},
            "header_time_spacing_seconds_counts": dict(sorted(header_tr_counts.items())),
            "sidecar_repetition_time_seconds_counts": dict(sorted(repetition_times.items())),
            "sidecar_fields_present": dict(sorted(sidecar_fields.items())),
        }

    return {
        "dataset_root_name": base.name,
        "source_provenance": {
            "name": description.get("Name"),
            "bids_version": description.get("BIDSVersion"),
            "license": description.get("License"),
            "dataset_doi": description.get("DatasetDOI"),
            "participants_tsv_sha256": sha256_file(participants_path),
            "dataset_description_sha256": sha256_file(description_path),
        },
        "participant_count": len(participants),
        "participant_group_counts": dict(sorted(groups.items())),
        "modalities": modality_summary,
        "participant_level_identifiers_emitted": False,
        "voxel_data_loaded": False,
    }
