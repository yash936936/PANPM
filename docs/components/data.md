# Component: data

> Location: `src/data/`. Generic Phase 0 inventory, source contracts, aggregate grain audits, explicit mapping configuration and aggregate feasibility-report functions are implemented; approved participant-level exports have not been inspected.

## Purpose

Import approved PPMI exports, normalize participant/visit/scan relationships, validate source mappings and create versioned cohort, modality and split manifests. This area owns data lineage and schema validation, not image processing or model training.

## Implemented utilities

- `source_mapping.py`: validates explicit mappings from source export columns to PANPM fields. It does not guess field names.
- `feasibility.py`: loads release-specific JSON mappings, normalizes explicitly mapped rows and computes aggregate cohort, MRI/image-manifest and medication-state progression coverage reports. It never emits participant IDs.
- `audit.py`: audits caller-specified candidate keys and child-to-parent relationships, returning aggregate counts only. Composite keys are held as ephemeral keyed digests in an in-memory SQLite database.
- `inventory.py`: discovers CSV exports recursively, skips hidden directories, reads headers, counts rows, summarizes missing values and records relative paths, file size, release identifier and SHA-256 checksum without retaining participant-level rows.
- `bids_inventory.py`: reads BIDS participants, dataset provenance, selected JSON sidecar fields and NIfTI-1 headers; emits aggregate T1w/BOLD coverage and geometry summaries without loading voxels or emitting participant IDs.
- `scripts/inventory_exports.py`: command-line entry point for metadata-only inventory. Keep output outside Git.
- `manifest.py`: creates keyed HMAC participant pseudonyms and aggregates series counts by supplied modality label. The HMAC secret remains outside Git.
- `schema.py`: defines PANPM internal table contracts and validates declared keys and participant links.
- `ppmi_contracts.py`: records selected source table fields from the supplied annotated PPMI dictionary and validates only documented linkage fields.
- `progression_targets.py`: selects a closest eligible motor assessment using an explicit target date, tolerance and exact normalized medication state; rejects ties and mixed-state score changes.

## PPMI source tables reviewed

See [`docs/ppmi-source-catalog.md`](../ppmi-source-catalog.md) for exact extracted definitions and caveats.

| Source table | Documented role | PANPM use |
|---|---|---|
| `PATIENT_STATUS` | Participant identity, cohort and enrollment status | Restricted participant/cohort source |
| `MRI` | MRI assessment at participant/event level | Assessment status and clinical MRI fields |
| `MRI_ACQUISITION` | Acquisition date, protocol, QC and sequence flags | Candidate modality/sequence metadata |
| `MRIQC` | T1-weighted MRIQC metrics | Image-level QC features, if present |
| `GMVOLUME` | Extracted grey-matter volume | Derived imaging feature, if present |
| `DTIROI` | DTI region-of-interest measurements | Derived diffusion feature, if present |
| `NUPDRS3TRT` | MDS-UPDRS Part III examination and treatment state | Longitudinal motor outcome, state-stratified |
| `LEDDLOG` | Levodopa-equivalent medication log | Time-aligned medication exposure |

## Route

1. Inventory the approved export tree and record the download date, release identifier and checksums.
2. Compare actual headers with the source catalog and `PPMI_SOURCE_TABLES`.
3. Review table grain and actual key cardinality before joining. Do not assume a one-row-per-participant/event rule solely from a field name.
4. Create explicit mappings into PANPM normalized tables and record unmatched rows.
5. Pseudonymize participant identifiers before ordinary analysis tables; keep the HMAC secret and crosswalk in restricted storage.
6. Build participant-by-sequence and participant-by-outcome coverage manifests before choosing model inputs.

## Invariants

- Raw exports are immutable and never committed.
- Data download date, release identifier and source checksums are recorded for every build.
- Missingness is retained and categorized rather than converted to zero.
- Joins validate cardinality and report unmatched rows.
- HMAC pseudonyms are linkage protection, not anonymization.
- All visits and scans from a participant remain in one split.
- Diagnosis labels and future progression outcomes are not exposed as RL observations.

## Known limits

No approved PPMI participant-level exports, LONI metadata or MRI files have been inspected. No real cohort counts, sequence coverage, scanner/site distribution or endpoint completeness has been computed. The example mapping is not validated against an actual release. The progression coverage function requires explicit source-state mapping, an allowed `PAG_NAME` form list, target states and date tolerance; it excludes ties and follow-up assessments not later than baseline. It does not settle clinical endpoint rules, derive time-aligned LEDD or define DBS eligibility. No image preprocessing, image QC, supervised models or RL has been implemented. The BIDS inventory parses NIfTI-1 headers only; it is not a full BIDS validator.

<!-- BEGIN GENERATED: do not edit between markers -->

### Files and exports

| File | Exports | Responsibility (first header-comment line) |
|---|---|---|
| `src/data/audit.py` | `audit_csv_keys`, `audit_csv_relationship` | Aggregate CSV key-grain and relationship audits without exposing identifiers. |
| `src/data/bids_inventory.py` | `read_nifti_header`, `inventory_bids_dataset` | Metadata-only BIDS inventory for local OpenNeuro development datasets. |
| `src/data/feasibility.py` | `load_mapping_config`, `validate_configured_header`, `normalize_configured_rows`, `cohort_coverage`, `mri_manifest_matching`, `progression_endpoint_coverage`, `build_phase0_report` | Build aggregate Phase 0 coverage reports from explicitly configured CSV exports. |
| `src/data/inventory.py` | `sha256_file`, `read_csv_header`, `inspect_csv`, `count_csv_rows`, `summarize_values`, `discover_csv_exports`, `inventory_csv_tree` | Inventory approved tabular exports and imaging metadata without loading images. |
| `src/data/manifest.py` | `pseudonymize`, `build_coverage_manifest` | Create pseudonymous participant coverage manifests from approved metadata. |
| `src/data/ppmi_contracts.py` | `PPMISourceTable`, `validate_ppmi_source_header` | Source-level contracts transcribed from the supplied PPMI reference files. |
| `src/data/progression_targets.py` | `MotorAssessment`, `AmbiguousAssessmentError`, `select_motor_assessment`, `motor_score_change` | Medication-state-aware selection helpers for longitudinal motor outcomes. |
| `src/data/schema.py` | `TableContract`, `ValidationIssue`, `validate_table`, `validate_participant_links` | Canonical PANPM table contracts and relational checks. |
| `src/data/source_mapping.py` | `MappingSpec` | Validate explicit mappings from source export columns to PANPM fields. |

**Imports other areas:** (none)

**Tests:** `tests/test_data_audit.py`, `tests/test_data_bids_inventory.py`, `tests/test_data_feasibility.py`, `tests/test_data_inventory.py`, `tests/test_data_manifest.py`, `tests/test_data_schema.py`, `tests/test_data_source_mapping.py`

<!-- END GENERATED -->

---
**Next:** Return to [`context.md`](../../context.md) before starting a new task.
