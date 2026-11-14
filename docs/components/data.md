# Component: data

> Location: `src/data/`. Planned source area; implementation is not present yet.

## Purpose

Import approved PPMI data exports, normalize participant/visit/scan relationships, validate source mappings and create versioned cohort, modality and split manifests. This area owns data lineage and schema validation, not image processing or model training.

## Route

The pipeline entry point will call the inventory/import functions first. Validated normalized tables feed cohort construction; the cohort manifest then feeds preprocessing and model datasets. No runtime route exists yet because source modules have not been implemented.

## Config surface and invariants

- Data release and source file checksums are mandatory.
- Participant keys used in analysis are pseudonymous.
- Source identifiers and mapping keys stay in restricted storage.
- Joins must validate expected cardinality and record unmatched rows.
- No source file is overwritten; raw data are immutable.
- Missingness is retained and categorized rather than silently converted to zero.

## Known limits

PPMI export field names, release version and actual modality coverage have not been inspected. Internal schema fields are proposed and must be mapped to the current data dictionary.

<!-- BEGIN GENERATED: do not edit between markers -->

### Files and exports

| File | Exports | Responsibility (first header-comment line) |
|---|---|---|

**Imports other areas:** (none)

**Tests:** (none matched by name)

<!-- END GENERATED -->

---
**Next:** Return to [`context.md`](../../context.md) before starting a new task.
