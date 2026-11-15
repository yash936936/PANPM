# BIDS metadata inventory

PANPM's local BIDS inventory reads only `participants.tsv`, selected JSON sidecar fields and the first 348 bytes of NIfTI-1 headers. It does not load voxel arrays. Its JSON report contains aggregate participant/group/modality counts, shape and voxel-spacing frequency tables, sidecar-field presence and invalid/missing-file counts. It does not emit participant identifiers or file paths.

## Requirements

- A locally downloaded BIDS dataset with `participants.tsv`.
- `participants.tsv` must contain `participant_id` and `group`.
- NIfTI-1 `.nii` or `.nii.gz` files for `*_T1w` and/or `*_bold` acquisitions.
- Python standard library only.

The inventory intentionally does not claim full BIDS-validator compliance. It does not currently parse NIfTI-2, read image data, validate affine orientation, inspect all BIDS entities, perform image QC or determine clinical suitability. A missing JSON sidecar is reported; a present sidecar is parsed and only a fixed allowlist of acquisition keys is summarized. Invalid sidecar JSON fails the run rather than being silently ignored.

## Run locally

Keep the downloaded dataset and output outside the Git worktree:

```bash
python scripts/inventory_bids.py \
  --root /data/openneuro/ds005892 \
  --output /secure/panpm-reports/ds005892-bids-inventory.json
```

The output is aggregate-only, but review the dataset's terms and local institutional requirements before sharing even aggregate results. Do not commit participant-level TSVs, sidecars, image files, manifests, source IDs or inventory outputs.

## Acceptance checks for Phase 0

1. Participant table parses with no duplicate or empty IDs.
2. Participant group counts reconcile with the versioned source table.
3. T1w and BOLD file counts and participant coverage are measured separately.
4. Unknown subject folders and participants missing each modality are counted.
5. NIfTI headers parse and shape/spacing distributions are recorded.
6. JSON sidecar presence and acquisition-field coverage are summarized.
7. Dataset version, license, download date, snapshot commit and source checksums are recorded separately.
8. Cohort split feasibility is assessed at participant level; no slice/patch/timepoint is treated as an independent participant.

A successful inventory is a metadata feasibility gate only. It does not authorize preprocessing, model training or clinical interpretation until geometry, QC, cohort rules and participant-level split feasibility have been reviewed.
---
**Next:** Return to [`context.md`](../context.md) before starting a new task.
