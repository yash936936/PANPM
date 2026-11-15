from __future__ import annotations

import gzip
import json
import struct

import pytest

from src.data.bids_inventory import inventory_bids_dataset, read_nifti_header


def _write_nifti(path, shape=(64, 64, 48), spacing=(1.0, 1.0, 1.5)):
    header = bytearray(348)
    struct.pack_into("<i", header, 0, 348)
    dims = (len(shape), *shape, *([1] * (7 - len(shape))))
    struct.pack_into("<8h", header, 40, *dims)
    pixdim = (1.0, *spacing, *([1.0] * (7 - len(spacing))))
    struct.pack_into("<8f", header, 76, *pixdim)
    struct.pack_into("<h", header, 70, 16)
    struct.pack_into("<h", header, 72, 32)
    struct.pack_into("<2h", header, 252, 1, 1)
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wb") as stream:
        stream.write(header)
        stream.write(b"\0" * 16)
    sidecar = path.with_suffix("").with_suffix(".json")
    sidecar.write_text(json.dumps({"RepetitionTime": 2.0, "Manufacturer": "Siemens"}))


def test_read_nifti_header_reads_geometry_without_voxels(tmp_path):
    image = tmp_path / "sub-001" / "anat" / "sub-001_T1w.nii.gz"
    _write_nifti(image)
    header = read_nifti_header(image)
    assert header["shape"] == [64, 64, 48]
    assert header["voxel_sizes_mm"] == [1.0, 1.0, 1.5]
    assert header["datatype"] == 16


def test_inventory_reports_aggregate_group_and_modality_coverage(tmp_path):
    (tmp_path / "dataset_description.json").write_text(
        json.dumps({"Name": "Synthetic", "BIDSVersion": "1.8.0", "License": "CC0", "DatasetDOI": "doi:test"})
    )
    (tmp_path / "participants.tsv").write_text(
        "participant_id\tgroup\nsub-001\tControl\nsub-002\tPD-NC\n",
        encoding="utf-8",
    )
    _write_nifti(tmp_path / "sub-001" / "anat" / "sub-001_T1w.nii.gz")
    _write_nifti(tmp_path / "sub-002" / "anat" / "sub-002_T1w.nii.gz")
    _write_nifti(tmp_path / "sub-001" / "func" / "sub-001_task-rest_bold.nii.gz", shape=(64, 64, 32, 120))
    report = inventory_bids_dataset(tmp_path)
    assert report["participant_count"] == 2
    assert report["source_provenance"]["license"] == "CC0"
    assert len(report["source_provenance"]["participants_tsv_sha256"]) == 64
    assert report["participant_group_counts"] == {"Control": 1, "PD-NC": 1}
    assert report["modalities"]["T1w"]["participant_count"] == 2
    assert report["modalities"]["bold"]["participant_count"] == 1
    assert report["modalities"]["bold"]["participants_without_file_count"] == 1
    assert report["participant_level_identifiers_emitted"] is False
    assert report["voxel_data_loaded"] is False


def test_duplicate_participant_ids_are_rejected(tmp_path):
    (tmp_path / "dataset_description.json").write_text(json.dumps({"Name": "Synthetic"}))
    (tmp_path / "participants.tsv").write_text(
        "participant_id\tgroup\nsub-001\tControl\nsub-001\tPD-NC\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="duplicate"):
        inventory_bids_dataset(tmp_path)


def test_invalid_nifti_header_is_rejected(tmp_path):
    image = tmp_path / "bad.nii.gz"
    with gzip.open(image, "wb") as stream:
        stream.write(b"bad")
    with pytest.raises(ValueError, match="Truncated"):
        read_nifti_header(image)
