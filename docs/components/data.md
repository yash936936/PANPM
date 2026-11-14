# Component: data

> Location: `src/data/`. Phase 0 metadata utilities are now present; PPMI-specific ingestion and cohort construction are not implemented.

## Purpose

Import approved PPMI data exports, normalize participant/visit/scan relationships, validate source mappings and create versioned cohort, modality and split manifests. This area owns data lineage and schema validation, not image processing or model training.

## Implemented utilities

- `source_mapping.py`: validates explicit source-to-normalized column mappings and required target fields. It does not guess PPMI field names.
- `inventory.py`: reads CSV headers, counts rows, summarizes missing values and records file size, release identifier and SHA-256 checksum.
- `manifest.py`: creates keyed HMAC participant pseudonyms and aggregates series counts by supplied modality label. The HMAC secret is supplied at runtime and must remain outside Git.

## Route

The planned pipeline inventories the approved exports first. A researcher reviews the actual headers and authors a mapping specification. Validated normalized tables then feed cohort construction; the cohort manifest feeds preprocessing and model datasets. No PPMI-specific mapping or MRI sequence classifier exists yet.

## Config surface and invariants

- Data release and source file checksums are mandatory.
- Participant keys used in analysis are pseudonymous.
- Source identifiers and mapping keys stay in restricted storage.
- Joins must validate expected cardinality and record unmatched rows.
- No source file is overwritten; raw data are immutable.
- Missingness is retained and categorized rather than silently converted to zero.
- HMAC secret material is not committed and pseudonyms are not treated as anonymization.

## Known limits

No PPMI export field names, release version, actual modality coverage or imaging metadata have been inspected. The current helpers are generic and have not been executed in a local repository checkout. They do not parse DICOM/NIfTI, align visits, select index dates, define outcomes or perform MRI quality control.

<!-- BEGIN GENERATED: do not edit between markers -->

### Files and exports

| File | Exports | Responsibility (first header-comment line) |
|---|---|---|
| `src/data/inventory.py` | `sha256_file`, `read_csv_header`, `inspect_csv`, `count_csv_rows`, `summarize_values` | Inventory approved tabular exports and imaging metadata without loading images. |
| `src/data/manifest.py` | `pseudonymize`, `build_coverage_manifest` | Create pseudonymous participant coverage manifests from approved metadata. |
| `src/data/source_mapping.py` | `MappingSpec` | Validate explicit mappings from source export columns to PANPM fields. |

**Imports other areas:** (none)

**Tests:** `tests/test_data_inventory.py`, `tests/test_data_manifest.py`, `tests/test_data_source_mapping.py`

<!-- END GENERATED -->

---
**Next:** Return to [`context.md`](../../context.md) before starting a new task.
