# Component: preprocessing

> Location: `src/preprocessing/`. Local-only DICOM header indexing and first-pass T1w voxel QC/montage generation are implemented in source; the local dataset has not yet been processed and full preprocessing remains unimplemented.

## Purpose

Convert and validate MRI series, identify sequence families from multiple metadata sources, perform modality-specific preprocessing, create anatomical segmentations and ROI masks, and produce auditable QC artifacts.

## Route

The initial route reads DICOM headers from a local ZIP without extracting pixel data, HMACs patient/study/series identifiers, and writes a private series-level manifest. The T1w QC route reads only explicitly sequence-verified scans from a private CSV manifest, calculates voxel intensity/finite-value/geometry summaries, writes pseudonymous private reports and native-orientation montages, and never modifies source images. It does not infer sequence family or select a scan. A reviewed release-specific mapping and image QC must precede conversion and feature extraction.

## Config surface and invariants

- Never modify raw DICOM/NIfTI inputs.
- Record software versions, parameters, checksums and output paths.
- Reject or quarantine ambiguous series instead of guessing their modality.
- Apply brain extraction, registration and segmentation QC before ROI features are used.
- A nonzero foreground proxy is not a brain mask or brain-volume estimate.
- QC thresholds are caller-supplied; flags request human review and never automatically exclude a scan.
- T1, DTI, neuromelanin, QSM and fMRI are conditional on verified data availability.
- A conventional T1 image must not be treated as a neuromelanin-sensitive image.

## Known limits

No PPMI series inventory, MRI files or segmentation QC data have been provided. The T1w QC code has synthetic tests pending CI but has not been run on ds005892. BOLD motion QC, visual review, brain extraction, registration and segmentation remain unimplemented.

<!-- BEGIN GENERATED: do not edit between markers -->

### Files and exports

| File | Exports | Responsibility (first header-comment line) |
|---|---|---|
| `src/preprocessing/mri_manifest.py` | `aggregate_header_rows`, `index_dicom_zip` | Local-only DICOM header indexing for PANPM MRI intake. |
| `src/preprocessing/qc.py` | `inspect_t1w`, `render_t1w_montage`, `aggregate_t1w_qc` | Voxel-level structural MRI QC metrics and private visual montages. |
| `scripts/qc_t1w.py` | `main` | Run private, non-destructive voxel-level QC on verified T1w scans. |

**Imports other areas:** (none)

**Tests:** `tests/test_preprocessing_qc.py`

<!-- END GENERATED -->

---
**Next:** Return to [`context.md`](../../context.md) before starting a new task.
