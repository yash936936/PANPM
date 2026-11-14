# Component: data

> Location: `src/data/`. Phase 0 utilities and source-independent table contracts are implemented; no PPMI exports have been inspected.

## Purpose

Import approved PPMI exports, normalize participant/visit/scan relationships, validate source mappings and create versioned cohort, modality and split manifests. This area owns data lineage and schema validation, not image processing or model training.

## Implemented utilities

- `source_mapping.py`: validates explicit mappings from source export columns to PANPM fields. It does not guess PPMI field names.
- `inventory.py`: discovers CSV exports recursively, skips hidden directories, reads headers, counts rows, summarizes missing values and records relative paths, file size, release identifier and SHA-256 checksum without loading participant-level values.\n- `scripts/inventory_exports.py`: command-line entry point for creating a JSON inventory from an approved local export directory; output contains metadata only.
- `manifest.py`: creates keyed HMAC participant pseudonyms and aggregates series counts by supplied modality label. The HMAC secret is supplied at runtime and must remain outside Git.
- `schema.py`: defines minimum required columns for the normalized participant, clinical visit, imaging scan, progression target and split tables; checks declared unique keys and participant foreign-key links. These are PANPM internal contracts, not claims about PPMI source headers.

## Route

Run `python scripts/inventory_exports.py --root /secure/path/to/exports --release-id <release-id> --output /secure/path/to/inventory.json` to create a metadata-only inventory. Keep the export root and inventory output outside the Git repository.\n\nThe planned pipeline inventories approved exports first. A researcher reviews the actual headers and authors a mapping specification. Mapped tables are checked against the internal contracts and participant links before cohort construction. No source-specific mapping, MRI sequence classifier or image parser exists.

## Config surface and invariants

- Data release and source file checksums are mandatory.
- Participant keys used in analysis are pseudonymous.
- Source identifiers and mapping keys stay in restricted storage.
- Joins must validate expected cardinality and record unmatched rows.
- No source file is overwritten; raw data are immutable.
- Missingness is retained and categorized rather than silently converted to zero.
- HMAC secret material is not committed and pseudonyms are not treated as anonymization.
- Clinical visit rows are not forced to be unique by participant and visit because multiple assessment states may exist.

## Known limits

No PPMI export field names, release version, actual modality coverage or imaging metadata have been inspected. The current helpers and contracts have not been executed in a local repository checkout. They do not parse DICOM/NIfTI, align visits, select index dates, define outcomes or perform MRI quality control.

<!-- BEGIN GENERATED: do not edit between markers -->

### Files and exports

| File | Exports | Responsibility (first header-comment line) |
|---|---|---|
| `src/data/inventory.py` | `sha256_file`, `read_csv_header`, `inspect_csv`, `count_csv_rows`, `summarize_values` | Inventory approved tabular exports and imaging metadata without loading images. |
| `src/data/manifest.py` | `pseudonymize`, `build_coverage_manifest` | Create pseudonymous participant coverage manifests from approved metadata. |
| `src/data/schema.py` | `CONTRACTS`, `TableContract`, `ValidationIssue`, `validate_table`, `validate_participant_links` | Define normalized PANPM table contracts and validate keys and participant links. |
| `src/data/source_mapping.py` | `MappingSpec` | Validate explicit mappings from source export columns to PANPM fields. |

**Imports other areas:** (none)

**Tests:** `tests/test_data_inventory.py`, `tests/test_data_manifest.py`, `tests/test_data_schema.py`, `tests/test_data_source_mapping.py`

<!-- END GENERATED -->

---
**Next:** Return to [`context.md`](../../context.md) before starting a new task.
