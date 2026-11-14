# Component: preprocessing

> Location: `src/preprocessing/`. Planned source area; implementation is not present yet.

## Purpose

Convert and validate MRI series, identify sequence families from multiple metadata sources, perform modality-specific preprocessing, create anatomical segmentations and ROI masks, and produce auditable QC artifacts.

## Route

The data inventory supplies scan records and restricted source paths. Sequence classification and DICOM validation precede modality-specific preprocessing. QC-approved derivatives and masks are passed to feature extraction under `src/models/`. No runtime route exists yet.

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

**Imports other areas:** (none)

**Tests:** (none matched by name)

<!-- END GENERATED -->

---
**Next:** Return to [`context.md`](../../context.md) before starting a new task.
