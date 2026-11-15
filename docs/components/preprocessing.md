# Component: preprocessing

> Location: `src/preprocessing/`. Initial local-only DICOM header indexing is implemented in `mri_manifest.py`; sequence classification, conversion and image preprocessing remain unimplemented.

## Purpose

Convert and validate MRI series, identify sequence families from multiple metadata sources, perform modality-specific preprocessing, create anatomical segmentations and ROI masks, and produce auditable QC artifacts.

## Route

The initial route reads DICOM headers from a local ZIP without extracting pixel data, HMACs patient/study/series identifiers, and writes a private series-level manifest. It does not infer sequence family or select a scan. A reviewed release-specific mapping and image QC must precede conversion and feature extraction.

## Config surface and invariants

- Never modify raw DICOM/NIfTI inputs.
- Record software versions, parameters, checksums and output paths.
- Reject or quarantine ambiguous series instead of guessing their modality.
- Apply brain extraction, registration and segmentation QC before ROI features are used.
- T1, DTI, neuromelanin, QSM and fMRI are conditional on verified data availability.
- A conventional T1 image must not be treated as a neuromelanin-sensitive image.

## Known limits

No PPMI series inventory, MRI files or segmentation QC data have been provided. Sequence mapping and preprocessing parameters remain to be tested on a representative pilot.

<!-- BEGIN GENERATED: do not edit between markers -->

### Files and exports

| File | Exports | Responsibility (first header-comment line) |
|---|---|---|
| `src/preprocessing/mri_manifest.py` | `aggregate_header_rows`, `index_dicom_zip` | Local-only DICOM header indexing for PANPM MRI intake. |

**Imports other areas:** (none)

**Tests:** (none matched by name)

<!-- END GENERATED -->

---
**Next:** Return to [`context.md`](../../context.md) before starting a new task.
