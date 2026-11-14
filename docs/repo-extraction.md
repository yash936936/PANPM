# Repository extraction and PPMI readiness

**Repository inspected:** `yash936936/PANPM`, branch `main`, commit `ffed36e37f3fde392c77ea315acccd11caff7c87` (2026-11-15).

This is an extraction of what exists in the repository. It is not evidence that PPMI participant data have been downloaded or analyzed.

## Implemented source-independent code

| File | Current responsibility | Evidence boundary |
|---|---|---|
| `src/data/inventory.py` | CSV discovery, header inspection, row counts, file size, SHA-256 and release metadata | Does not load MRI or compute participant-level cohort statistics |
| `scripts/inventory_exports.py` | CLI for metadata-only CSV inventory | Output must stay outside Git |
| `src/data/source_mapping.py` | Explicit source-column to normalized-field mapping | Does not infer field mappings |
| `src/data/manifest.py` | HMAC pseudonyms and participant-by-modality series counts | Requires caller-supplied field names and secret; HMAC is not anonymization |
| `src/data/schema.py` | Internal PANPM table contracts, unique-key checks and participant foreign-key checks | Does not validate every PPMI source table |
| `src/data/ppmi_contracts.py` | Selected PPMI source field contracts | Derived from supplied reference docs, not verified exports |
| `src/data/progression_targets.py` | Exact-state, caller-window motor assessment selection and score-change helper | Does not map source codes, set clinical windows, derive LEDD or resolve DBS rules |

## PPMI source tables represented in the repository

| Source table | Fields the repo records | Intended use |
|---|---|---|
| `PATIENT_STATUS` | `PATNO`, `COHORT`, `COHORT_DEFINITION`, `ENROLL_STATUS`, `ENROLL_DATE`, `ENROLL_AGE`, `STATUS_DATE`, `REC_ID` | Participant/cohort status |
| `MRI` | `PATNO`, `EVENT_ID`, `INFODT`, `MRICMPLT`, `MRIRSLT`, `MRIRSSDF`, `MRIWDTI`, `MRIWRSS`, medication date/time, `REC_ID` | MRI assessment and visit linkage |
| `MRI_ACQUISITION` | `PATNO`, `EVENT_ID`, `MRI_SCAN_DATE`, `PROTOCOL`, analysis/QC fields, T1/T2/DTI/resting-state/neuromelanin-MT sequence flags, scanner-change fields | Acquisition-level sequence audit |
| `MRIQC` | `PATNO`, `EVENT_ID`, filename and MRIQC metrics such as `cnr`, `efc`, `fber`, `fwhm_avg`, SNR and tissue-volume metrics | Image QC, subject to actual key/grain audit |
| `GMVOLUME` | `PATNO`, `EVENT_ID`, `IMAGEID`, `MRIDATE`, `GM_VOLUME` | Grey-matter volume feature |
| `DTIROI` | `PATNO`, `IMAGE_ID`, `INFODT`, `Measure`, `Tissue`, `REF1`, `REF2`, `ROI1`-`ROI6`, `RUNDATE` | Diffusion ROI feature |
| `NUPDRS3TRT` | `NP3TOT`, `PDSTATE`, `ONOFFORDER`, `PDMEDYN`, `PDTRTMNT`, medication date/time, `HRPOSTMED`, DBS fields, `PAG_NAME`, `EXAMDT`, `EXAMTM`, `REC_ID` | State-aware motor outcomes |
| `LEDDLOG` | `LEDTRT`, `LEDD`, dose fields, `STARTDT`, `STOPDT`, `TOTDDA`, `REC_ID` | Time-aligned medication exposure |

## Internal normalized tables specified

The repository's `docs/data-dictionary.md` specifies these target artifacts:

- `participants.parquet`: one row per pseudonymous participant.
- `clinical_visits.parquet`: one row per participant, event and assessment-state record.
- `imaging_scans.parquet`: one row per MRI series/acquisition.
- `roi_features.parquet`: one row per scan, atlas region, feature and feature version.
- `progression_targets.parquet`: one row per participant, horizon and medication-state definition.
- `gene_risk.parquet` and `atlas_expression.parquet`: traceable genetic evidence and reference expression.
- `regional_genetic_prior.parquet`: population-level regional prior, not participant genotype.
- `rl_episodes.parquet`: one row per action in a participant/task episode, with reward separated from policy observations.
- `split_manifest.parquet`: immutable participant-level split assignments.

These are target schemas, not existing populated datasets.

## Planned but not implemented

The directories `src/preprocessing/`, `src/models/`, `src/genetics/`, `src/rl/`, `src/evaluation/` and `src/visualization/` contain no implementation modules in the inspected tree. The architecture and research protocol specify future components, including MRI sequence validation, segmentation, ROI features, diagnosis/progression predictors, regional priors and masked PPO.

## First-week PPMI ingestion sequence

1. Preserve the original approved download in restricted, read-only storage. Record access terms, download timestamp, release identifier and archive checksums.
2. Run the CSV inventory script on the export tree. Keep inventory outputs and raw files outside Git.
3. Compare actual headers against the source catalog. Save a release-specific schema diff.
4. Measure each table's row count, null keys, candidate key uniqueness, duplicate rows and participant/event/image linkage cardinality before joining.
5. Build participant coverage for PD/HC and separate cohorts; preserve SWEDD, prodromal and genetic registry categories in the source layer.
6. Join MRI assessment records to acquisition metadata and LONI image manifests. Treat sequence flags as leads, not proof that an image file exists.
7. Determine verified MRI sequence coverage from metadata and DICOM headers. Do not select T1 or advanced modalities until the coverage/QC matrix is measured.
8. Audit `NUPDRS3TRT` form/state completeness, `NP3TOT` validity, medication timing, DBS status and `LEDDLOG` intervals. Freeze the 12/24-month endpoint only after this audit.
9. Build participant-level overlap matrices: MRI sequence x diagnosis; MRI sequence x valid motor outcome; and baseline MRI x 12/24-month target.
10. Freeze cohort rules, mappings, target definition and subject-level split manifest. Only then start preprocessing and baseline models.

## Current verification status

- PR #1, #2 and #3 are merged into `main`.
- CI on the current main merge commit was inspected. It is failing in three jobs: Python setup cannot find a default pip cache dependency file; component docs are stale; secret scan flags a fake key literal inside the self-test source. The failing steps were inspected in workflow logs.
- The workflow has not reached Ruff or pytest because Python setup exits before dependency installation.
- No claim is made that repository tests passed locally.
- No PPMI participant-level data, MRI image files or LONI image manifests are present in this repository.

---
**Next:** Return to [`context.md`](../context.md) before starting a new task.
