# BIDS metadata inventory and NIfTI geometry audit

PANPM's local BIDS inventory reads `dataset_description.json`, `participants.tsv`, selected JSON sidecar fields and the first 348 bytes of NIfTI-1 headers. It does not load voxel arrays. Its JSON report contains aggregate participant/group/modality counts, shape distributions, spatial voxel spacing, header temporal spacing, sidecar repetition-time distributions, affine validity, orientation codes, qform/sform disagreement counts, provenance and source-table checksums. It does not emit participant identifiers or file paths.

## Requirements

- A locally downloaded BIDS dataset with `participants.tsv`.
- `participants.tsv` must contain `participant_id` and `group`.
- NIfTI-1 `.nii` or `.nii.gz` files for `*_T1w` and/or `*_bold` acquisitions.
- Python standard library only.

## Geometry fields

- `spatial_voxel_spacing_mm_counts` contains only the first three NIfTI spatial dimensions.
- `header_time_spacing_seconds_counts` reports NIfTI `pixdim[4]` for 4D images.
- `sidecar_repetition_time_seconds_counts` reports BIDS JSON `RepetitionTime`.
- The affine is selected from sform, then qform, then a flagged spacing-only fallback.
- `affine_valid` checks finite matrix values and a non-singular 3x3 spatial transform.
- `orientation_code_counts` reports the closest cardinal RAS+ axis labels.
- `qform_sform_disagreement_count` counts coded transforms differing by more than 0.001 in any matrix element.

Orientation codes are a metadata screen, not a substitute for visual inspection or registration QC. The fallback affine cannot establish anatomical orientation. NIfTI-2 is not supported.

## Run locally

Keep the downloaded dataset and output outside both the PANPM worktree and the source BIDS directory:

```powershell
py scripts/inventory_bids.py `
  --root D:\PANPM-data\ds005892 `
  --output D:\PANPM-data\ds005892-inventory-geometry.json
```

The output is aggregate-only, but review the dataset's terms and local institutional requirements before sharing even aggregate results. Do not commit participant-level TSVs, sidecars, image files, manifests, source IDs or inventory outputs.

## Acceptance checks for Phase 0

1. Participant table parses with no duplicate or empty IDs.
2. Participant group counts reconcile with the versioned source table.
3. T1w and BOLD file counts and participant coverage are measured separately.
4. Unknown subject folders and participants missing each modality are counted.
5. NIfTI headers parse and spatial/time spacing distributions are separated.
6. Coded affine matrices are finite and non-singular; orientation and qform/sform differences are summarized.
7. JSON sidecar presence and acquisition-field coverage are summarized.
8. Dataset version, license, download date, snapshot commit and source checksums are recorded separately.
9. Cohort split feasibility is assessed at participant level; no slice/patch/timepoint is treated as an independent participant.

A successful inventory is a metadata feasibility gate only. It does not establish image quality, registration quality, clinical suitability, progression endpoint coverage or permission to train a model.
---
**Next:** Return to [`context.md`](../context.md) before starting a new task.
