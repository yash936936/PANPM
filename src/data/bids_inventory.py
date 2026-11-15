"""Metadata-only BIDS inventory for local OpenNeuro development datasets.

Reads participants.tsv, BIDS JSON sidecars and NIfTI headers. It never loads
voxel arrays and emits aggregate summaries only. Keep the BIDS tree local.
"""
from __future__ import annotations

import csv
import gzip
import json
import struct
from collections import Counter, defaultdict
from pathlib import Path
from typing import BinaryIO

MODALITY_PATTERNS = {
    "T1w": "*_T1w.nii*",
    "bold": "*_bold.nii*",
}
SIDECAR_KEYS = (
    "Manufacturer",
    "ManufacturersModelName",
    "MagneticFieldStrength",
    "RepetitionTime",
    "EchoTime",
    "FlipAngle",
    "PhaseEncodingDirection",
    "TotalReadoutTime",
    "SliceTiming",
)


def _open_nifti(path: Path) -> BinaryIO:
    return gzip.open(path, "rb") if path.name.endswith(".gz") else path.open("rb")


def read_nifti_header(path: str | Path) -> dict[str, object]:
    """Read NIfTI-1 header dimensions and voxel sizes without reading voxels."""
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
    if any(value <= 0 for value in pixdim[1 : ndim + 1]):
        raise ValueError(f"Invalid NIfTI voxel spacing: {file_path.name}")
    datatype = struct.unpack_from(f"{endian}h", header, 70)[0]
    bitpix = struct.unpack_from(f"{endian}h", header, 72)[0]
    qform_code, sform_code = struct.unpack_from(f"{endian}2h", header, 252)
    return {
        "ndim": ndim,
        "shape": list(dims[1 : ndim + 1]),
        "voxel_sizes_mm": [round(abs(v), 5) for v in pixdim[1 : ndim + 1]],
        "datatype": datatype,
        "bitpix": bitpix,
        "qform_code": qform_code,
        "sform_code": sform_code,
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
        raise ValueError(f"BIDS JSON sidecar must contain an object: {sidecar.name}")
    return {key: payload[key] for key in SIDECAR_KEYS if key in payload}


def inventory_bids_dataset(root: str | Path) -> dict[str, object]:
    """Return aggregate-only participant/modality and NIfTI metadata summaries."""
    base = Path(root)
    if not base.is_dir():
        raise NotADirectoryError(f"BIDS root is not a directory: {base}")
    participants = _read_participants(base / "participants.tsv")
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
                if not subject_dirs:
                    continue
                files_by_modality[modality][subject_dirs[0]].append(path)

    modality_summary: dict[str, object] = {}
    for modality, by_subject in files_by_modality.items():
        known = set(by_subject) & set(participants)
        unknown = set(by_subject) - set(participants)
        group_coverage = Counter(participants[subject] for subject in known)
        headers: list[dict[str, object]] = []
        sidecar_fields: Counter[str] = Counter()
        invalid_headers = 0
        missing_sidecars = 0
        for subject_files in by_subject.values():
            for image_path in subject_files:
                try:
                    headers.append(read_nifti_header(image_path))
                except (OSError, ValueError, EOFError):
                    invalid_headers += 1
                metadata = _sidecar(image_path)
                if not metadata:
                    missing_sidecars += 1
                sidecar_fields.update(metadata.keys())
        shape_counts = Counter(tuple(item["shape"]) for item in headers)
        spacing_counts = Counter(tuple(item["voxel_sizes_mm"]) for item in headers)
        modality_summary[modality] = {
            "file_count": sum(len(paths) for paths in by_subject.values()),
            "participant_count": len(known),
            "participant_count_by_group": dict(sorted(group_coverage.items())),
            "participants_without_file_count": len(set(participants) - known),
            "files_for_unknown_participant_count": sum(len(by_subject[s]) for s in unknown),
            "invalid_nifti_header_count": invalid_headers,
            "missing_or_empty_sidecar_count": missing_sidecars,
            "header_shape_counts": {str(k): v for k, v in sorted(shape_counts.items())},
            "voxel_spacing_mm_counts": {str(k): v for k, v in sorted(spacing_counts.items())},
            "sidecar_fields_present": dict(sorted(sidecar_fields.items())),
        }

    return {
        "dataset_root_name": base.name,
        "participant_count": len(participants),
        "participant_group_counts": dict(sorted(groups.items())),
        "modalities": modality_summary,
        "participant_level_identifiers_emitted": False,
        "voxel_data_loaded": False,
    }
