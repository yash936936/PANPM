# Status - PANPM

> Running project log. Newest entry goes at the top. Update this file at the end of every work session.

## 2026-11-15 - Official PPMI reference documents extracted; MRI source catalog added
**Current phase:** Phase 0 - PPMI access and feasibility audit. Reference-document review is complete for the supplied files; participant-level feasibility audit remains blocked on approved exports.
**Branch:** `research/phase0-ppmi-dictionary`.
**Previous PR:** #1 was merged into `main`; this work is on a new branch from `main`.
**Last debug:** `DBG-006` - extracted PPMI guide, annotated dictionary and code list; tests authored but not run.
**Last decisions:** `D-011` - preserve PPMI cohort categories and unresolved dictionary/guide differences.

**Inspected:** PPMI Data User Guide (cover updated August 6, 2026), Annotated Data Dictionary (May 23, 2025), and Annotated Code List (May 23, 2025). The guide's introduction contains an older August 28, 2024 revision note; the discrepancy is recorded in the source catalog.

**Added:** `docs/ppmi-source-catalog.md` documents participant/cohort fields, MRI and MRI_ACQUISITION fields, MRI sequence flags, MRIQC metrics, GMVOLUME, DTIROI, code values and known documentation conflicts. `src/data/ppmi_contracts.py` adds conservative source contracts for selected tables; `tests/test_ppmi_contracts.py` adds synthetic header-validation tests.

**Important findings:** The dictionary defines T1-weighted, T2-FLAIR, DTI, resting-state fMRI and neuromelanin MT acquisition flags. It also lists MRIQC metrics, grey-matter volume extraction and DTI ROI measures. The Code List has cohort codes 1, 2, 3, 4, 7 and 8; the guide's five-cohort description and dictionary's genetic registry categories are not identical. The source catalog preserves this discrepancy rather than silently reconciling it.

**Not verified:** approved PPMI access, participant-level CSV exports, LONI imaging metadata, actual image files, MRI coverage, sequence prevalence, scanner/site distributions, endpoint completeness, preprocessing, models, RL, local pytest/Ruff or CI. No participant counts or scientific results have been computed.

**Next:** obtain approved PPMI access and export the relevant Participant Status, MRI, MRI Acquisition, MRIQC and clinical assessment tables plus imaging metadata. Run the metadata-only inventory outside Git, then reconcile real headers and row grains against these source contracts before creating final mappings.

---

**Next:** Return to [`context.md`](../context.md) before starting a new task.


## 2026-11-15 - Public PPMI tooling reviewed; recursive CSV discovery added
**Current phase:** Phase 0 - PPMI access and feasibility audit (software scaffold only; no PPMI data available).
**Branch:** `research/phase0-repository-audit`.
**Last debug:** `DBG-004` - public tooling review and CSV tree inventory; tests authored but not executed.
**Last decisions:** `D-010` - upstream tooling treated as reference, not source truth.

**Reviewed:** public documentation and code from MJFF Research Community PIE, PIE-clean, NetNeuroLab markello_ppmisnf, and the official PPMI Data Resources page. Added `docs/external-references.md` with source links, reusable patterns and cautions. In particular, upstream PIE warns against relying only on LONI's Weighting label for T1 selection; PANPM will verify acquisition metadata and DICOM headers against the actual release before sequence selection.

**Created:** `discover_csv_exports` and `inventory_csv_tree` recursively enumerate CSV exports and record relative path, header, row count, size and SHA-256 without loading participant-level rows. Added synthetic tests.

**Not verified:** local pytest, Ruff, CI, official PPMI field mappings, actual export headers, participant counts, MRI coverage, endpoint completeness, image QC, preprocessing, model training, RL behaviour or scientific results.

**Next up:** obtain official PPMI Data Dictionary, Code List and Data User Guide from the Data Resources page; once downloaded, inspect and extract their actual definitions. Obtain approved access before using participant-level exports or images.

---
**Next:** Return to [`context.md`](../context.md) before starting a new task.

## 2026-11-15 - Schema validation privacy hardening
Updated `src/data/schema.py` so duplicate-key validation errors no longer print the duplicate key itself. Added a synthetic regression test. This is a privacy hardening change only; no PPMI fields or records were processed.

**Verification:** Tests have been authored but not executed. No local checkout or verified CI run is available.

## 2026-11-15 - Added local inventory command
Added `scripts/inventory_exports.py`, a standard-library CLI that calls the metadata-only CSV inventory and writes JSON to stdout or a user-selected path. Documented invocation and the requirement to keep both raw exports and generated inventory outside Git. The command has not been executed in a local checkout; tests and lint remain unverified.
