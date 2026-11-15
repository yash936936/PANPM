"""Local-only DICOM header indexing for PANPM MRI intake.

This module reads metadata only. It never extracts pixel data or writes raw
participant identifiers. Run it only in an institution-approved environment
for datasets whose terms permit this processing.
"""
from __future__ import annotations

import hashlib
import hmac
import io
import zipfile
from collections import Counter, defaultdict
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any


_HEADER_FIELDS = (
    "Modality",
    "SeriesDescription",
    "ProtocolName",
    "SequenceName",
    "ImageType",
    "MRAcquisitionType",
    "Manufacturer",
    "ManufacturerModelName",
    "MagneticFieldStrength",
    "StudyDate",
    "SeriesDate",
    "AcquisitionDate",
    "Rows",
    "Columns",
    "PixelSpacing",
    "SliceThickness",
    "SpacingBetweenSlices",
    "NumberOfFrames",
    "InstanceNumber",
    "SOPInstanceUID",
    "SeriesInstanceUID",
    "StudyInstanceUID",
    "PatientID",
)


def _text(value: object) -> str:
    """Convert a DICOM value to stable plain text without retaining DICOM objects."""
    if value is None:
        return ""
    if isinstance(value, (list, tuple)):
        return "\\".join(str(part) for part in value)
    return str(value).strip()


def _digest(value: str, secret: bytes, namespace: str) -> str:
    if len(secret) < 32:
        raise ValueError("HMAC secret must contain at least 32 bytes")
    if not value.strip():
        raise ValueError("Cannot pseudonymize an empty identifier")
    message = f"panpm-mri-v1:{namespace}:{value.strip()}".encode("utf-8")
    return hmac.new(secret, message, hashlib.sha256).hexdigest()


def _is_original(image_type: str) -> bool | None:
    tokens = {part.strip().upper() for part in image_type.split("\\") if part.strip()}
    if not tokens:
        return None
    return "ORIGINAL" in tokens and not bool(tokens.intersection({"DERIVED", "SECONDARY"}))


def aggregate_header_rows(
    header_rows: Iterable[Mapping[str, object]],
    *,
    secret: bytes,
) -> dict[str, Any]:
    """Aggregate instance headers into pseudonymous series-level metadata.

    Sequence family is deliberately not inferred from filenames, LONI
    Weighting labels, or description text. A series is only marked as a
    3-D MR acquisition when the corresponding DICOM header explicitly says so.
    """
    if len(secret) < 32:
        raise ValueError("HMAC secret must contain at least 32 bytes")

    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    counters: Counter[str] = Counter()
    seen_sops: set[str] = set()

    for raw in header_rows:
        counters["header_rows"] += 1
        row = {field: _text(raw.get(field)) for field in _HEADER_FIELDS}
        patient_id = row["PatientID"]
        series_uid = row["SeriesInstanceUID"]
        study_uid = row["StudyInstanceUID"]
        if not patient_id:
            counters["missing_patient_id"] += 1
            continue
        if not series_uid:
            counters["missing_series_uid"] += 1
            continue
        if not study_uid:
            counters["missing_study_uid"] += 1
            continue

        sop_uid = row["SOPInstanceUID"]
        if sop_uid and sop_uid in seen_sops:
            counters["duplicate_sop_instance_uid"] += 1
        elif sop_uid:
            seen_sops.add(sop_uid)

        participant_key = _digest(patient_id, secret, "participant")
        series_key = _digest(series_uid, secret, "series")
        study_key = _digest(study_uid, secret, "study")
        groups[series_key].append({
            **row,
            "participant_key": participant_key,
            "series_key": series_key,
            "study_key": study_key,
        })
        counters["indexed_instances"] += 1

    series: list[dict[str, Any]] = []
    for series_key, instances in sorted(groups.items()):
        first = instances[0]
        participant_keys = {r["participant_key"] for r in instances}
        study_keys = {r["study_key"] for r in instances}
        if len(participant_keys) != 1 or len(study_keys) != 1:
            counters["series_identity_conflicts"] += 1
            continue

        def unique_values(field: str) -> list[str]:
            return sorted({r[field] for r in instances if r[field]})

        conflicts = {
            field: values
            for field in (
                "Modality",
                "SeriesDescription",
                "ProtocolName",
                "SequenceName",
                "MRAcquisitionType",
                "Manufacturer",
                "ManufacturerModelName",
                "MagneticFieldStrength",
                "StudyDate",
                "SeriesDate",
                "AcquisitionDate",
                "Rows",
                "Columns",
                "PixelSpacing",
                "SliceThickness",
                "SpacingBetweenSlices",
                "NumberOfFrames",
            )
            if len(values := unique_values(field)) > 1
        }
        modality_values = unique_values("Modality")
        acquisition_values = unique_values("MRAcquisitionType")
        image_type_values = unique_values("ImageType")
        is_mr = modality_values == ["MR"]
        is_3d = acquisition_values == ["3D"] if acquisition_values else None
        original_flags = {_is_original(v) for v in image_type_values}
        is_original = original_flags.pop() if len(original_flags) == 1 else None

        reasons = []
        if not is_mr:
            reasons.append("modality_not_unambiguously_mr")
        if is_3d is not True:
            reasons.append("acquisition_not_unambiguously_3d")
        if is_original is not True:
            reasons.append("image_type_not_unambiguously_original")
        if conflicts:
            reasons.append("intra_series_header_conflict")
        if not first["Rows"] or not first["Columns"]:
            reasons.append("missing_image_dimensions")

        series.append({
            "participant_key": first["participant_key"],
            "study_key": first["study_key"],
            "series_key": series_key,
            "instance_count": len(instances),
            "modality": modality_values[0] if len(modality_values) == 1 else None,
            "series_description": first["SeriesDescription"] or None,
            "protocol_name": first["ProtocolName"] or None,
            "sequence_name": first["SequenceName"] or None,
            "image_type": image_type_values,
            "acquisition_type": acquisition_values[0] if len(acquisition_values) == 1 else None,
            "manufacturer": unique_values("Manufacturer"),
            "manufacturer_model": unique_values("ManufacturerModelName"),
            "magnetic_field_strength_t": unique_values("MagneticFieldStrength"),
            "study_dates": unique_values("StudyDate"),
            "series_dates": unique_values("SeriesDate"),
            "acquisition_dates": unique_values("AcquisitionDate"),
            "rows": unique_values("Rows"),
            "columns": unique_values("Columns"),
            "pixel_spacing": unique_values("PixelSpacing"),
            "slice_thickness_mm": unique_values("SliceThickness"),
            "spacing_between_slices_mm": unique_values("SpacingBetweenSlices"),
            "number_of_frames": unique_values("NumberOfFrames"),
            "is_mr": is_mr,
            "is_3d": is_3d,
            "is_original": is_original,
            "sequence_family": None,
            "selection_status": "needs_sequence_review",
            "qc_status": "header_review_required" if reasons else "header_checks_passed",
            "qc_reasons": reasons,
            "header_conflicts": conflicts,
        })

    return {
        "schema_version": "panpm-mri-series-manifest-v1",
        "source_scope": "DICOM headers only; pixel data not read",
        "sequence_family_policy": "not_inferred; requires reviewed release-specific mapping",
        "counts": dict(sorted(counters.items())),
        "series_count": len(series),
        "series": series,
    }


def index_dicom_zip(
    archive_path: str | Path,
    *,
    secret: bytes,
) -> dict[str, Any]:
    """Read DICOM headers from a local ZIP archive without extracting pixel data.

    Requires pydicom in the local imaging environment. Archive member names and
    raw DICOM identifiers are not returned in the manifest.
    """
    try:
        import pydicom
    except ImportError as exc:
        raise RuntimeError(
            "DICOM header indexing requires pydicom in the local imaging environment"
        ) from exc

    rows = []
    unreadable = 0
    with zipfile.ZipFile(archive_path) as archive:
        for member in archive.infolist():
            if member.is_dir():
                continue
            try:
                dataset = pydicom.dcmread(
                    io.BytesIO(archive.read(member)),
                    stop_before_pixels=True,
                    force=False,
                )
            except Exception:
                unreadable += 1
                continue
            row = {}
            for field in _HEADER_FIELDS:
                value = getattr(dataset, field, None)
                if field == "ImageType" and value is not None:
                    row[field] = "\\\\".join(str(part) for part in value)
                elif field == "PixelSpacing" and value is not None:
                    row[field] = "\\\\".join(str(part) for part in value)
                else:
                    row[field] = _text(value)
            rows.append(row)

    result = aggregate_header_rows(rows, secret=secret)
    result["archive_name"] = Path(archive_path).name
    result["counts"]["unreadable_archive_members"] = unreadable
    result["counts"]["archive_members_examined"] = len(rows) + unreadable
    return result
