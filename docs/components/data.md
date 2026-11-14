# Component: data

> Location: `src/data/`. Generic Phase 0 inventory utilities and conservative PPMI source contracts are implemented; approved participant-level exports have not been inspected.

## Purpose

Import approved PPMI exports, normalize participant/visit/scan relationships, validate source mappings and create versioned cohort, modality and split manifests. This area owns data lineage and schema validation, not image processing or model training.

## Implemented utilities

- `source_mapping.py`: validates explicit mappings from source export columns to PANPM fields. It does not guess field names.
- `inventory.py`: discovers CSV exports recursively, skips hidden directories, reads headers, counts rows, summarizes missing values and records relative paths, file size, release identifier and SHA-256 checksum without retaining participant-level rows.
- `scripts/inventory_exports.py`: command-line entry point for metadata-only inventory. Keep output outside Git.
- `manifest.py`: creates keyed HMAC participant pseudonyms and aggregates series counts by supplied modality label. The HMAC secret remains outside Git.
- `schema.py`: defines PANPM internal table contracts and validates declared keys and participant links.
- `ppmi_contracts.py`: records selected source table fields from the supplied annotated PPMI dictionary and validates only documented participant/visit linkage fields. It does not enforce ambiguous uniqueness declarations or infer data availability.

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

The guide and code list contain differences in cohort descriptions. Preserve the original source values and define a versioned analytic cohort rule separately.

## Route

1. Inventory the approved export tree and record the download date, release identifier and checksums.
2. Compare actual headers with the source catalog and `PPMI_SOURCE_TABLES`.
3. Review table grain and actual key cardinality before joining. Do not assume a one-row-per-participant/event rule solely from a field name.
4. Create explicit mappings into PANPM normalized tables and record unmatched rows.
5. Pseudonymize participant identifiers before ordinary analysis tables; keep the HMAC secret and crosswalk in restricted storage.
6. Build participant-by-sequence coverage and outcome completeness manifests before choosing model inputs.

## Invariants

- Raw exports are immutable and never committed.
- Data download date, release identifier and source checksums are recorded for every build.
- Missingness is retained and categorized rather than converted to zero.
- Joins validate cardinality and report unmatched rows.
- HMAC pseudonyms are linkage protection, not anonymization.
- All visits and scans from a participant remain in one split.
- Diagnosis labels and future progression outcomes are not exposed as RL observations.

## Known limits

No approved PPMI participant-level exports, LONI metadata or MRI files have been inspected. No cohort counts, sequence coverage, scanner/site distribution or endpoint completeness has been computed. The source contracts are based on reference-document definitions only. They do not parse DICOM/NIfTI, determine MRI sequence identity, align progression visits, define the final analytic cohort or run QC.

<!-- BEGIN GENERATED: do not edit between markers -->

### Files and exports

| File | Exports | Responsibility |
|---|---|---|
| `src/data/inventory.py` | CSV inventory helpers | Metadata-only export inventory |
| `src/data/manifest.py` | `pseudonymize`, `build_coverage_manifest` | Pseudonymous participant and modality coverage |
| `src/data/ppmi_contracts.py` | `PPMI_SOURCE_TABLES`, `validate_ppmi_source_header` | Conservative source-table contracts |
| `src/data/schema.py` | `CONTRACTS`, `validate_table`, `validate_participant_links` | PANPM normalized schema contracts |
| `src/data/source_mapping.py` | `MappingSpec` | Explicit source-column mappings |

**Tests:** `tests/test_data_inventory.py`, `tests/test_data_manifest.py`, `tests/test_data_schema.py`, `tests/test_data_source_mapping.py`, `tests/test_ppmi_contracts.py`

<!-- END GENERATED -->

---
**Next:** Return to [`context.md`](../../context.md) before starting a new task.
